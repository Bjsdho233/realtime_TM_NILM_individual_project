from __future__ import annotations

import importlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import fastrand
import numpy as np
import pandas as pd
from bitarray import bitarray
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


ROOT = Path(__file__).resolve().parents[1]
HAN_ROOT = ROOT / "han-nilm-inspection"
DATA_ROOT = ROOT / "t3-minimal-repro-run" / "temp"
OUTPUT_PATH = ROOT / "tmp" / "tm_mechanism_probe_results.json"

sys.path.insert(0, str(HAN_ROOT))

from tsetlin import Tsetlin  # noqa: E402
from tsetlin.utils.booleanize import booleanize_features  # noqa: E402


CLASSES = ["fridge", "microwave", "dish washer", "electric furnace"]
TRAIN_HOUSES = [1, 2, 4, 5, 6]
TEST_HOUSES = [3]

FEATURES = ["transition", "duration"]
FEATURES += [
    "pos_transition_magnitude",
    "neg_transition_magnitude",
    "abs_transition",
    "log_abs_transition",
    "duration",
    "log_duration",
    "transition_duration_product",
    "transition_duration_ratio",
    "episode_mean_main",
    "episode_std_main",
    "episode_min_main",
    "episode_max_main",
    "episode_range_main",
    "internal_diff_mean_abs",
    "internal_diff_max_abs",
    "internal_edge_count",
    "subcycle_count_proxy",
    "active_fraction_proxy",
    "episode_energy_estimate",
    "post_minus_pre_mean",
    "event_internal_edge_count",
]

VARIANTS = [
    {"name": "baseline", "T": 20, "negative_mode": "random", "shuffle": False},
    {"name": "T10", "T": 10, "negative_mode": "random", "shuffle": False},
    {"name": "shuffle", "T": 20, "negative_mode": "random", "shuffle": True},
    {"name": "hard50", "T": 20, "negative_mode": "hard50", "shuffle": False},
    {"name": "hard100", "T": 20, "negative_mode": "hard", "shuffle": False},
]


def disable_progress_bars() -> None:
    identity = lambda values, **_: values
    importlib.import_module("tsetlin.tsetlin").tqdm = identity
    importlib.import_module("tsetlin.utils.booleanize").tqdm = identity


def load_events(houses: list[int]) -> tuple[np.ndarray, np.ndarray]:
    frames = []
    labels = {name: index for index, name in enumerate(CLASSES)}

    for house in houses:
        for appliance in CLASSES:
            path = DATA_ROOT / f"building_{house}_{appliance}_matched_transitions.csv"
            if not path.exists():
                continue
            try:
                frame = pd.read_csv(path)
            except pd.errors.EmptyDataError:
                continue
            frame = frame.copy()
            frame["label"] = labels[appliance]
            frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    return data[FEATURES].to_numpy(dtype=float), data["label"].to_numpy(dtype=int)


def prepare_boolean_data() -> tuple[list[bitarray], np.ndarray, list[bitarray], np.ndarray]:
    x_train, y_train = load_events(TRAIN_HOUSES)
    x_test, y_test = load_events(TEST_HOUSES)

    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    train_bool = booleanize_features(x_train.copy(), mean, std, num_bits=8)
    test_bool = booleanize_features(x_test.copy(), mean, std, num_bits=8)

    train_bits = [bitarray(list(map(bool, row))) for row in train_bool]
    test_bits = [bitarray(list(map(bool, row))) for row in test_bool]
    return train_bits, y_train, test_bits, y_test


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    fastrand.pcg32_seed(seed)


def class_outputs(model: Tsetlin, x: bitarray, class_index: int) -> tuple[list[int], list[int], int]:
    positive = [clause.evaluate(x) for clause in model.pos_clauses[class_index]]
    negative = [clause.evaluate(x) for clause in model.neg_clauses[class_index]]
    return positive, negative, sum(positive) - sum(negative)


def choose_negative(model: Tsetlin, x: bitarray, target: int, mode: str) -> int:
    candidates = [index for index in range(model.n_classes) if index != target]
    if mode == "random":
        return random.choice(candidates)
    if mode == "hard50" and random.random() > 0.5:
        return random.choice(candidates)

    votes = {index: class_outputs(model, x, index)[2] for index in candidates}
    highest = max(votes.values())
    tied = [index for index, vote in votes.items() if vote == highest]
    return random.choice(tied)


def pairwise_step(model: Tsetlin, x: bitarray, target: int, T: int, s: float, mode: str) -> None:
    positive, negative, class_sum = class_outputs(model, x, target)
    class_sum = np.clip(class_sum, -T, T)
    target_probability = (T - class_sum) / (2 * T)

    for index in range(model.n_clauses // 2):
        if random.random() <= target_probability:
            model.pos_clauses[target][index].type_I_feedback(x, positive[index], s=s)
        if negative[index] == 1 and random.random() <= target_probability:
            model.neg_clauses[target][index].type_II_feedback(x)

    other = choose_negative(model, x, target, mode)
    positive, negative, class_sum = class_outputs(model, x, other)
    class_sum = np.clip(class_sum, -T, T)
    negative_probability = (T + class_sum) / (2 * T)

    for index in range(model.n_clauses // 2):
        if positive[index] == 1 and random.random() <= negative_probability:
            model.pos_clauses[other][index].type_II_feedback(x)
        if random.random() <= negative_probability:
            model.neg_clauses[other][index].type_I_feedback(x, negative[index], s=s)


def state_signature(model: Tsetlin) -> tuple[int, ...]:
    states = []
    for class_index in range(model.n_classes):
        for positive, negative in zip(
            model.pos_clauses[class_index], model.neg_clauses[class_index]
        ):
            states.extend(positive.get_state())
            states.extend(negative.get_state())
    return tuple(states)


def verify_random_step(x_train: list[bitarray], y_train: np.ndarray) -> None:
    seed_all(137)
    upstream = Tsetlin(184, len(CLASSES), 20, 50)
    for x, target in zip(x_train[:20], y_train[:20]):
        upstream.step(x, int(target), T=20, s=6.0)

    seed_all(137)
    probe = Tsetlin(184, len(CLASSES), 20, 50)
    for x, target in zip(x_train[:20], y_train[:20]):
        pairwise_step(probe, x, int(target), T=20, s=6.0, mode="random")

    if state_signature(upstream) != state_signature(probe):
        raise RuntimeError("Probe random-negative update does not match upstream Tsetlin.step")


def clause_summary(model: Tsetlin) -> dict[str, float]:
    signatures = []
    lengths = []
    for class_index in range(model.n_classes):
        for clause in model.pos_clauses[class_index] + model.neg_clauses[class_index]:
            lengths.append(clause.p_included_mask.count() + clause.n_included_mask.count())
            signatures.append(
                (clause.p_included_mask.tobytes(), clause.n_included_mask.tobytes())
            )
    counts = Counter(signatures)
    return {
        "mean_literals": float(np.mean(lengths)),
        "median_literals": float(np.median(lengths)),
        "empty_clause_fraction": float(np.mean(np.asarray(lengths) == 0)),
        "unique_clause_fraction": len(counts) / len(signatures),
    }


def vote_summary(model: Tsetlin, x_test: list[bitarray], y_test: np.ndarray) -> dict[str, float]:
    _, votes = model.predict(x_test, return_votes=True)
    margins = []
    saturated = 0
    for row, target in zip(votes, y_test):
        target_vote = row[int(target)]
        other_vote = max(vote for index, vote in enumerate(row) if index != int(target))
        margins.append(target_vote - other_vote)
        saturated += int(any(abs(vote) >= 20 for vote in row))
    return {
        "mean_true_margin": float(np.mean(margins)),
        "median_true_margin": float(np.median(margins)),
        "negative_margin_fraction": float(np.mean(np.asarray(margins) < 0)),
        "vote_ge_20_fraction": saturated / len(votes),
    }


def run_variant(
    variant: dict[str, object],
    seed: int,
    x_train: list[bitarray],
    y_train: np.ndarray,
    x_test: list[bitarray],
    y_test: np.ndarray,
) -> dict[str, object]:
    seed_all(seed)
    model = Tsetlin(184, len(CLASSES), 200, 50)
    shuffle_rng = np.random.default_rng(seed + 10_000)
    start = time.perf_counter()

    for _ in range(10):
        order = np.arange(len(x_train))
        if variant["shuffle"]:
            shuffle_rng.shuffle(order)
        for row_index in order:
            pairwise_step(
                model,
                x_train[row_index],
                int(y_train[row_index]),
                T=int(variant["T"]),
                s=6.0,
                mode=str(variant["negative_mode"]),
            )

    training_seconds = time.perf_counter() - start
    prediction = np.asarray(model.predict(x_test), dtype=int)
    class_f1 = f1_score(y_test, prediction, labels=np.arange(len(CLASSES)), average=None)

    return {
        "variant": variant["name"],
        "seed": seed,
        "T": variant["T"],
        "negative_mode": variant["negative_mode"],
        "shuffle": variant["shuffle"],
        "accuracy": float(accuracy_score(y_test, prediction)),
        "macro_f1": float(np.mean(class_f1)),
        "class_f1": {name: float(score) for name, score in zip(CLASSES, class_f1)},
        "confusion_matrix": confusion_matrix(
            y_test, prediction, labels=np.arange(len(CLASSES))
        ).tolist(),
        "training_seconds": training_seconds,
        "clauses": clause_summary(model),
        "votes": vote_summary(model, x_test, y_test),
    }


def aggregate(runs: list[dict[str, object]]) -> dict[str, object]:
    summary = {}
    for variant in [item["name"] for item in VARIANTS]:
        selected = [run for run in runs if run["variant"] == variant]
        macro = np.asarray([run["macro_f1"] for run in selected])
        accuracy = np.asarray([run["accuracy"] for run in selected])
        summary[variant] = {
            "macro_f1_mean": float(np.mean(macro)),
            "macro_f1_std": float(np.std(macro, ddof=1)),
            "accuracy_mean": float(np.mean(accuracy)),
            "accuracy_std": float(np.std(accuracy, ddof=1)),
            "class_f1_mean": {
                name: float(np.mean([run["class_f1"][name] for run in selected]))
                for name in CLASSES
            },
            "mean_literals": float(
                np.mean([run["clauses"]["mean_literals"] for run in selected])
            ),
            "mean_true_margin": float(
                np.mean([run["votes"]["mean_true_margin"] for run in selected])
            ),
        }
    return summary


def main() -> None:
    disable_progress_bars()
    x_train, y_train, x_test, y_test = prepare_boolean_data()
    verify_random_step(x_train, y_train)

    print(
        f"train={len(x_train)} test={len(x_test)} features={len(x_train[0])} "
        f"train_counts={np.bincount(y_train).tolist()} test_counts={np.bincount(y_test).tolist()}"
    )

    runs = []
    for variant in VARIANTS:
        for seed in [0, 1, 2]:
            result = run_variant(variant, seed, x_train, y_train, x_test, y_test)
            runs.append(result)
            print(
                f"{result['variant']:>8} seed={seed} "
                f"acc={result['accuracy']:.4f} macro_f1={result['macro_f1']:.4f} "
                f"seconds={result['training_seconds']:.2f}"
            )

    output = {
        "scope": {
            "purpose": "exploratory_tm_mechanism_probe",
            "formal_model_selection": False,
            "classes": CLASSES,
            "train_houses": TRAIN_HOUSES,
            "test_houses": TEST_HOUSES,
            "feature_slots": len(FEATURES),
            "boolean_inputs": len(x_train[0]),
            "clauses": 200,
            "states": 50,
            "specificity_s": 6.0,
            "epochs": 10,
            "seeds": [0, 1, 2],
        },
        "runs": runs,
        "summary": aggregate(runs),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"saved={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
