from __future__ import annotations

import argparse
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


OUTPUT_PATH = ROOT / "tmp" / "tm_balance_sweep_results.json"
DEFAULT_ALPHAS = [1.0, 0.75, 0.5, 0.25, 0.0]
DEFAULT_SEEDS = [0, 1, 2, 3, 4]


def largest_remainder_counts(class_counts: np.ndarray, alpha: float) -> np.ndarray:
    """Convert n_c ** alpha into integer class quotas with a fixed total."""
    weights = class_counts.astype(float) ** alpha
    expected = weights / np.sum(weights) * np.sum(class_counts)
    quotas = np.floor(expected).astype(int)
    remaining = int(np.sum(class_counts) - np.sum(quotas))

    if remaining:
        fractions = expected - quotas
        order = np.argsort(-fractions, kind="stable")
        quotas[order[:remaining]] += 1
    return quotas


def power_sample_order(
    labels: np.ndarray,
    alpha: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample a fixed number of rows using class probability P(c) proportional to n_c**alpha."""
    by_class = [np.flatnonzero(labels == index) for index in range(len(CLASSES))]
    class_counts = np.asarray([len(indices) for indices in by_class], dtype=int)
    quotas = largest_remainder_counts(class_counts, alpha)

    sampled = [
        rng.choice(indices, size=int(quota), replace=True)
        for indices, quota in zip(by_class, quotas)
    ]
    order = np.concatenate(sampled)
    rng.shuffle(order)
    return order, quotas


def coverage_preserving_order(
    labels: np.ndarray,
    alpha: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply class quotas while avoiding duplicates unless a class is oversampled."""
    by_class = [np.flatnonzero(labels == index) for index in range(len(CLASSES))]
    class_counts = np.asarray([len(indices) for indices in by_class], dtype=int)
    quotas = largest_remainder_counts(class_counts, alpha)

    # Alpha=1 must be exactly the ordinary shuffled-data control.
    if np.array_equal(quotas, class_counts):
        return shuffled_unique_order(labels, rng)

    sampled = []
    for indices, quota in zip(by_class, quotas):
        quota = int(quota)
        if quota <= len(indices):
            rows = rng.choice(indices, size=quota, replace=False)
        else:
            extra = rng.choice(indices, size=quota - len(indices), replace=True)
            rows = np.concatenate([rng.permutation(indices), extra])
        sampled.append(rows)

    order = np.concatenate(sampled)
    rng.shuffle(order)
    return order, quotas


def shuffled_unique_order(
    labels: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Shuffle all original rows once without changing the class distribution."""
    order = np.arange(len(labels))
    rng.shuffle(order)
    return order, np.bincount(labels, minlength=len(CLASSES))


def run_variant(
    name: str,
    alpha: float | None,
    seed: int,
    epochs: int,
    sampling_mode: str,
    x_train,
    y_train: np.ndarray,
    x_test,
    y_test: np.ndarray,
) -> dict[str, object]:
    seed_all(seed)
    model = Tsetlin(184, len(CLASSES), 200, 50)
    order_rng = np.random.default_rng(seed + 30_000)
    quota_history = []
    start = time.perf_counter()

    for _ in range(epochs):
        if alpha is None:
            order, quotas = shuffled_unique_order(y_train, order_rng)
        elif sampling_mode == "coverage":
            order, quotas = coverage_preserving_order(y_train, alpha, order_rng)
        else:
            order, quotas = power_sample_order(y_train, alpha, order_rng)
        quota_history.append(quotas.tolist())

        for row_index in order:
            pairwise_step(
                model,
                x_train[row_index],
                int(y_train[row_index]),
                T=20,
                s=6.0,
                mode="random",
            )

    training_seconds = time.perf_counter() - start
    prediction = np.asarray(model.predict(x_test), dtype=int)
    class_f1 = f1_score(
        y_test,
        prediction,
        labels=np.arange(len(CLASSES)),
        average=None,
        zero_division=0,
    )
    return {
        "variant": name,
        "alpha": alpha,
        "seed": seed,
        "accuracy": float(accuracy_score(y_test, prediction)),
        "macro_f1": float(np.mean(class_f1)),
        "class_f1": {name: float(score) for name, score in zip(CLASSES, class_f1)},
        "confusion_matrix": confusion_matrix(
            y_test, prediction, labels=np.arange(len(CLASSES))
        ).tolist(),
        "updates_per_epoch": int(len(y_train)),
        "class_updates_per_epoch": quota_history[0],
        "training_seconds": training_seconds,
        "clauses": clause_summary(model),
        "votes": vote_summary(model, x_test, y_test),
    }


def summarize(runs: list[dict[str, object]]) -> dict[str, object]:
    output = {}
    variants = list(dict.fromkeys(str(run["variant"]) for run in runs))
    for variant in variants:
        selected = sorted(
            [run for run in runs if run["variant"] == variant],
            key=lambda run: int(run["seed"]),
        )
        macro = np.asarray([run["macro_f1"] for run in selected], dtype=float)
        accuracy = np.asarray([run["accuracy"] for run in selected], dtype=float)
        output[variant] = {
            "alpha": selected[0]["alpha"],
            "class_updates_per_epoch": selected[0]["class_updates_per_epoch"],
            "macro_f1_mean": float(np.mean(macro)),
            "macro_f1_std": float(np.std(macro, ddof=1)),
            "macro_f1_by_seed": macro.tolist(),
            "accuracy_mean": float(np.mean(accuracy)),
            "accuracy_std": float(np.std(accuracy, ddof=1)),
            "accuracy_by_seed": accuracy.tolist(),
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
            "training_seconds_mean": float(
                np.mean([run["training_seconds"] for run in selected])
            ),
        }
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alphas", nargs="+", type=float, default=DEFAULT_ALPHAS)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument(
        "--sampling-mode",
        choices=["replacement", "coverage"],
        default="replacement",
    )
    parser.add_argument("--skip-shuffle-control", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    disable_progress_bars()
    x_train, y_train, x_test, y_test = prepare_boolean_data()
    verify_random_step(x_train, y_train)

    class_counts = np.bincount(y_train, minlength=len(CLASSES))
    variants = []
    if not args.skip_shuffle_control:
        variants.append(("shuffle_unique", None))
    variants.extend((f"alpha_{alpha:g}", alpha) for alpha in args.alphas)

    print(
        f"train={len(y_train)} test={len(y_test)} "
        f"class_counts={class_counts.tolist()} epochs={args.epochs} seeds={args.seeds}",
        flush=True,
    )
    for name, alpha in variants:
        quotas = class_counts if alpha is None else largest_remainder_counts(class_counts, alpha)
        print(f"variant={name} class_updates={quotas.tolist()}", flush=True)

    runs = []
    for name, alpha in variants:
        for seed in args.seeds:
            result = run_variant(
                name,
                alpha,
                seed,
                args.epochs,
                args.sampling_mode,
                x_train,
                y_train,
                x_test,
                y_test,
            )
            runs.append(result)
            print(
                f"{name:>14} seed={seed} acc={result['accuracy']:.4f} "
                f"macro_f1={result['macro_f1']:.4f} "
                f"seconds={result['training_seconds']:.2f}",
                flush=True,
            )

    output = {
        "scope": {
            "purpose": "exploratory_partial_class_balance_sweep",
            "formal_model_selection": False,
            "sampling_rule": "P(class) proportional to class_count ** alpha",
            "within_class_sampling": args.sampling_mode,
            "fixed_updates_per_epoch": int(len(y_train)),
            "classes": CLASSES,
            "train_counts": class_counts.tolist(),
            "T": 20,
            "specificity_s": 6.0,
            "clauses": 200,
            "states": 50,
            "epochs": args.epochs,
            "seeds": args.seeds,
        },
        "runs": runs,
        "summary": summarize(runs),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], indent=2), flush=True)
    print(f"saved={args.output}", flush=True)


if __name__ == "__main__":
    main()
