from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tmp"))

from tm_mechanism_probe import (  # noqa: E402
    CLASSES,
    Tsetlin,
    clause_summary,
    disable_progress_bars,
    pairwise_step,
    prepare_boolean_data,
    seed_all,
    verify_random_step,
    vote_summary,
)


OUTPUT_PATH = ROOT / "tmp" / "tm_mechanism_followup_results.json"

VARIANTS = [
    {"name": "shuffle_hard100", "negative_mode": "hard", "order_mode": "shuffle"},
    {"name": "balanced", "negative_mode": "random", "order_mode": "balanced"},
    {"name": "balanced_hard100", "negative_mode": "hard", "order_mode": "balanced"},
]


def epoch_order(mode: str, labels: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    if mode == "shuffle":
        order = np.arange(len(labels))
        rng.shuffle(order)
        return order

    if mode == "balanced":
        by_class = [np.flatnonzero(labels == index) for index in range(len(CLASSES))]
        class_sequence = np.resize(np.arange(len(CLASSES)), len(labels))
        rng.shuffle(class_sequence)
        return np.asarray([rng.choice(by_class[index]) for index in class_sequence])

    raise ValueError(f"Unknown order mode: {mode}")


def run_variant(variant, seed, x_train, y_train, x_test, y_test):
    seed_all(seed)
    model = Tsetlin(184, len(CLASSES), 200, 50)
    order_rng = np.random.default_rng(seed + 20_000)
    start = time.perf_counter()

    for _ in range(10):
        for row_index in epoch_order(variant["order_mode"], y_train, order_rng):
            pairwise_step(
                model,
                x_train[row_index],
                int(y_train[row_index]),
                T=20,
                s=6.0,
                mode=variant["negative_mode"],
            )

    training_seconds = time.perf_counter() - start
    prediction = np.asarray(model.predict(x_test), dtype=int)
    class_f1 = f1_score(y_test, prediction, labels=np.arange(len(CLASSES)), average=None)
    return {
        "variant": variant["name"],
        "seed": seed,
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


def summarize(runs):
    output = {}
    for variant in [item["name"] for item in VARIANTS]:
        selected = [run for run in runs if run["variant"] == variant]
        macro = np.asarray([run["macro_f1"] for run in selected])
        accuracy = np.asarray([run["accuracy"] for run in selected])
        output[variant] = {
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
    return output


def main() -> None:
    disable_progress_bars()
    x_train, y_train, x_test, y_test = prepare_boolean_data()
    verify_random_step(x_train, y_train)

    runs = []
    for variant in VARIANTS:
        for seed in [0, 1, 2]:
            result = run_variant(variant, seed, x_train, y_train, x_test, y_test)
            runs.append(result)
            print(
                f"{result['variant']:>16} seed={seed} "
                f"acc={result['accuracy']:.4f} macro_f1={result['macro_f1']:.4f} "
                f"seconds={result['training_seconds']:.2f}",
                flush=True,
            )

    output = {
        "scope": {
            "purpose": "exploratory_tm_mechanism_followup",
            "formal_model_selection": False,
            "T": 20,
            "specificity_s": 6.0,
            "epochs": 10,
            "seeds": [0, 1, 2],
            "updates_per_epoch": len(x_train),
            "balanced_sampling": "uniform classes with replacement at fixed update count",
        },
        "runs": runs,
        "summary": summarize(runs),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(f"saved={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
