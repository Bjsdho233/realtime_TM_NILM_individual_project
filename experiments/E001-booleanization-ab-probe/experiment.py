import csv
import hashlib
import json
import math
import os
import random
import statistics
import struct
import sys
import time
from pathlib import Path

os.environ.setdefault("TQDM_DISABLE", "1")

HAN_ROOT = Path(r"${HAN_UPSTREAM_ROOT}")
DATA_ROOT = Path(r"${MATCHED_EVENT_ROOT}")
OUTPUT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(HAN_ROOT))

import fastrand
import numpy as np
import pandas as pd
from bitarray import bitarray
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from tsetlin import Tsetlin
from tsetlin.utils.booleanize import booleanize_features

HOUSES = [1, 3, 5, 6]
CLASSES = ["fridge", "microwave", "dish washer", "electric furnace"]
CLASS_TO_ID = {name: index for index, name in enumerate(CLASSES)}
FEATURES = [
    "transition",
    "duration",
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
SEEDS = [0, 1, 2, 3, 4]
QUANTILES = np.arange(1, 9, dtype=float) / 9.0
N_CLAUSE = 200
N_STATE = 50
T = 20
S = 6.0
EPOCHS = 10


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(values):
    digest = hashlib.sha256()
    for value in values:
        digest.update(str(value).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_split():
    train_frames = []
    validation_frames = []
    files = []
    small_files = []
    missing_files = []

    for house in HOUSES:
        for appliance in CLASSES:
            path = DATA_ROOT / f"building_{house}_{appliance}_matched_transitions.csv"
            if not path.exists():
                missing_files.append({"house": house, "appliance": appliance})
                continue
            frame = pd.read_csv(path)
            required = set(FEATURES + ["start"])
            missing_columns = sorted(required - set(frame.columns))
            if missing_columns:
                raise RuntimeError(f"{path} lacks columns: {missing_columns}")
            frame = frame.sort_values("start", kind="mergesort").reset_index(drop=True)
            frame["_house"] = house
            frame["_appliance"] = appliance
            frame["_label"] = CLASS_TO_ID[appliance]
            frame["_source_index"] = np.arange(len(frame), dtype=int)
            frame["_row_id"] = [
                f"H{house}|{appliance}|{index}|{start!r}"
                for index, start in enumerate(frame["start"].tolist())
            ]

            if len(frame) < 5:
                cut = len(frame)
                small_files.append(
                    {
                        "house": house,
                        "appliance": appliance,
                        "events": len(frame),
                        "handling": "all retained in training",
                    }
                )
            else:
                cut = int(math.floor(0.8 * len(frame)))

            train = frame.iloc[:cut].copy()
            validation = frame.iloc[cut:].copy()
            train_frames.append(train)
            if len(validation):
                validation_frames.append(validation)
            files.append(
                {
                    "house": house,
                    "appliance": appliance,
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "events": len(frame),
                    "train_events": len(train),
                    "validation_events": len(validation),
                    "split_index": cut,
                    "sorted_by": "start ascending, stable mergesort",
                }
            )

    train = pd.concat(train_frames, ignore_index=True)
    validation = pd.concat(validation_frames, ignore_index=True)
    validation_classes = sorted(validation["_appliance"].unique().tolist())
    if validation_classes != sorted(CLASSES):
        raise RuntimeError(
            f"Validation lacks one or more classes: observed {validation_classes}"
        )

    x_train = train[FEATURES].to_numpy(dtype=float)
    x_validation = validation[FEATURES].to_numpy(dtype=float)
    y_train = train["_label"].to_numpy(dtype=int)
    y_validation = validation["_label"].to_numpy(dtype=int)
    if not np.isfinite(x_train).all() or not np.isfinite(x_validation).all():
        raise RuntimeError("Raw feature matrix contains NaN or infinity")

    return {
        "train": train,
        "validation": validation,
        "x_train": x_train,
        "x_validation": x_validation,
        "y_train": y_train,
        "y_validation": y_validation,
        "files": files,
        "small_files": small_files,
        "missing_files": missing_files,
    }


def encode_han_binary(x_train, x_validation):
    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    if not np.isfinite(mean).all() or not np.isfinite(std).all():
        raise RuntimeError("han_binary fitted mean/std is not finite")
    if np.any(std == 0):
        indices = np.flatnonzero(std == 0).tolist()
        raise RuntimeError(f"han_binary has zero training std at slots {indices}")
    train = np.asarray(
        booleanize_features(x_train.copy(), mean, std, num_bits=8), dtype=np.uint8
    )
    validation = np.asarray(
        booleanize_features(x_validation.copy(), mean, std, num_bits=8),
        dtype=np.uint8,
    )
    return train, validation, {
        "fit_scope": "training rows only",
        "mean": mean.tolist(),
        "std": std.tolist(),
        "levels_per_feature_at_most": 256,
    }


def encode_threshold_8(x_train, x_validation):
    thresholds = np.quantile(
        x_train, QUANTILES, axis=0, method="linear"
    )
    if not np.isfinite(thresholds).all():
        raise RuntimeError("threshold_8 fitted thresholds are not finite")
    threshold_by_feature = thresholds.T
    train = (
        x_train[:, :, None] >= threshold_by_feature[None, :, :]
    ).reshape(len(x_train), -1).astype(np.uint8)
    validation = (
        x_validation[:, :, None] >= threshold_by_feature[None, :, :]
    ).reshape(len(x_validation), -1).astype(np.uint8)
    repeated_thresholds = int(
        sum(8 - len(np.unique(threshold_by_feature[index])) for index in range(23))
    )
    return train, validation, {
        "fit_scope": "training rows only",
        "quantiles": QUANTILES.tolist(),
        "numpy_quantile_method": "linear",
        "thresholds_by_feature": threshold_by_feature.tolist(),
        "repeated_threshold_count": repeated_thresholds,
        "levels_per_feature_at_most": 9,
    }


def to_bitarrays(matrix):
    if matrix.shape[1] != 184:
        raise RuntimeError(f"Expected 184 bits, observed {matrix.shape[1]}")
    if not np.isfinite(matrix).all():
        raise RuntimeError("Encoded matrix contains NaN or infinity")
    if not np.isin(matrix, [0, 1]).all():
        raise RuntimeError("Encoded matrix contains non-Boolean values")
    return [bitarray(row.astype(bool).tolist()) for row in matrix]


def model_state_sha256(model):
    digest = hashlib.sha256()
    for groups in [model.pos_clauses, model.neg_clauses]:
        for class_clauses in groups:
            for clause in class_clauses:
                for state in clause.get_state():
                    digest.update(struct.pack("<i", int(state)))
    return digest.hexdigest()


def train_once(encoding, seed, x_train, y_train, x_validation, y_validation):
    random.seed(seed)
    fastrand.pcg32_seed(seed)
    shuffle_rng = np.random.default_rng(seed)
    model = Tsetlin(
        N_feature=184,
        N_class=4,
        N_clause=N_CLAUSE,
        N_state=N_STATE,
    )
    initial_state_sha256 = model_state_sha256(model)
    started = time.perf_counter()
    for _epoch in range(EPOCHS):
        order = shuffle_rng.permutation(len(y_train))
        if len(np.unique(order)) != len(y_train):
            raise RuntimeError("Epoch shuffle is not a unique permutation")
        for index in order:
            model.step(x_train[int(index)], int(y_train[int(index)]), T=T, s=S)
    training_seconds = time.perf_counter() - started
    prediction = np.asarray(model.predict(x_validation), dtype=int)
    class_f1 = f1_score(
        y_validation, prediction, labels=[0, 1, 2, 3], average=None, zero_division=0
    )
    row = {
        "encoding": encoding,
        "seed": seed,
        "accuracy": float(accuracy_score(y_validation, prediction)),
        "macro_f1": float(
            f1_score(
                y_validation,
                prediction,
                labels=[0, 1, 2, 3],
                average="macro",
                zero_division=0,
            )
        ),
        "fridge_f1": float(class_f1[0]),
        "microwave_f1": float(class_f1[1]),
        "dish_washer_f1": float(class_f1[2]),
        "electric_furnace_f1": float(class_f1[3]),
        "confusion_matrix": json.dumps(
            confusion_matrix(
                y_validation, prediction, labels=[0, 1, 2, 3]
            ).tolist(),
            separators=(",", ":"),
        ),
        "training_seconds": training_seconds,
        "initial_state_sha256": initial_state_sha256,
        "final_state_sha256": model_state_sha256(model),
    }
    return row, prediction.tolist()


def metric_summary(rows, encoding):
    selected = [row for row in rows if row["encoding"] == encoding]
    metrics = [
        "accuracy",
        "macro_f1",
        "fridge_f1",
        "microwave_f1",
        "dish_washer_f1",
        "electric_furnace_f1",
        "training_seconds",
    ]
    return {
        metric: {
            "mean": statistics.mean(float(row[metric]) for row in selected),
            "sample_std": statistics.stdev(float(row[metric]) for row in selected),
        }
        for metric in metrics
    }


def main():
    dataset = load_split()
    encoded = {}
    fits = {}
    han_train, han_validation, han_fit = encode_han_binary(
        dataset["x_train"], dataset["x_validation"]
    )
    encoded["han_binary"] = (han_train, han_validation)
    fits["han_binary"] = han_fit
    threshold_train, threshold_validation, threshold_fit = encode_threshold_8(
        dataset["x_train"], dataset["x_validation"]
    )
    encoded["threshold_8"] = (threshold_train, threshold_validation)
    fits["threshold_8"] = threshold_fit

    bitarrays = {}
    for encoding, (train_matrix, validation_matrix) in encoded.items():
        if train_matrix.shape != (len(dataset["y_train"]), 184):
            raise RuntimeError(f"{encoding} training shape mismatch")
        if validation_matrix.shape != (len(dataset["y_validation"]), 184):
            raise RuntimeError(f"{encoding} validation shape mismatch")
        bitarrays[encoding] = (
            to_bitarrays(train_matrix),
            to_bitarrays(validation_matrix),
        )

    train_row_ids = dataset["train"]["_row_id"].tolist()
    validation_row_ids = dataset["validation"]["_row_id"].tolist()
    rows = []
    predictions = {}
    initial_hashes = {}
    for seed in SEEDS:
        for encoding in ["han_binary", "threshold_8"]:
            train_bits, validation_bits = bitarrays[encoding]
            row, prediction = train_once(
                encoding,
                seed,
                train_bits,
                dataset["y_train"],
                validation_bits,
                dataset["y_validation"],
            )
            rows.append(row)
            predictions[f"{encoding}:{seed}"] = prediction
            initial_hashes.setdefault(seed, {})[encoding] = row["initial_state_sha256"]
        if initial_hashes[seed]["han_binary"] != initial_hashes[seed]["threshold_8"]:
            raise RuntimeError(f"Paired seed {seed} did not produce equal TM initialization")

    reproducibility = {}
    for encoding in ["han_binary", "threshold_8"]:
        original = next(
            row for row in rows if row["encoding"] == encoding and row["seed"] == 0
        )
        repeat, repeat_prediction = train_once(
            encoding,
            0,
            bitarrays[encoding][0],
            dataset["y_train"],
            bitarrays[encoding][1],
            dataset["y_validation"],
        )
        comparison_keys = [
            "accuracy",
            "macro_f1",
            "fridge_f1",
            "microwave_f1",
            "dish_washer_f1",
            "electric_furnace_f1",
            "confusion_matrix",
            "initial_state_sha256",
            "final_state_sha256",
        ]
        reproducibility[encoding] = {
            "seed": 0,
            "metrics_and_state_identical": all(
                original[key] == repeat[key] for key in comparison_keys
            ),
            "predictions_identical": predictions[f"{encoding}:0"]
            == repeat_prediction,
            "repeat_training_seconds": repeat["training_seconds"],
        }
        if not (
            reproducibility[encoding]["metrics_and_state_identical"]
            and reproducibility[encoding]["predictions_identical"]
        ):
            raise RuntimeError(f"Fixed-seed reproducibility failed for {encoding}")

    csv_fields = [
        "encoding",
        "seed",
        "accuracy",
        "macro_f1",
        "fridge_f1",
        "microwave_f1",
        "dish_washer_f1",
        "electric_furnace_f1",
        "confusion_matrix",
        "training_seconds",
        "initial_state_sha256",
        "final_state_sha256",
    ]
    with open(OUTPUT_ROOT / "per_seed_metrics.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(rows)

    by_encoding_seed = {
        (row["encoding"], row["seed"]): row for row in rows
    }
    deltas = [
        by_encoding_seed[("threshold_8", seed)]["macro_f1"]
        - by_encoding_seed[("han_binary", seed)]["macro_f1"]
        for seed in SEEDS
    ]
    wins = sum(delta > 0 for delta in deltas)
    losses = sum(delta < 0 for delta in deltas)
    ties = sum(delta == 0 for delta in deltas)
    mean_delta = statistics.mean(deltas)
    if mean_delta >= 0.02 and wins >= 4:
        decision = "promising"
    elif mean_delta > 0:
        decision = "inconclusive"
    else:
        decision = "not supported"

    summary = {
        "experiment": "E001 Booleanization A/B Probe",
        "status": "complete",
        "evidential_scope": "exploratory only; not formal model selection or final thesis evidence",
        "paths": {
            "scratch": str(OUTPUT_ROOT),
            "han_source": str(HAN_ROOT),
            "matched_event_source": str(DATA_ROOT),
            "python": sys.executable,
        },
        "contract": {
            "houses": HOUSES,
            "sealed_houses_not_read": [2, 4],
            "classes": CLASSES,
            "class_mapping": CLASS_TO_ID,
            "ordered_features": FEATURES,
            "feature_slots": len(FEATURES),
            "unique_features": len(set(FEATURES)),
            "input_bits": 184,
            "n_class": 4,
            "n_clause": N_CLAUSE,
            "n_state": N_STATE,
            "T": T,
            "s": S,
            "epochs": EPOCHS,
            "seeds": SEEDS,
            "shuffle": "one unique permutation of all raw training events per epoch",
        },
        "data": {
            "files": dataset["files"],
            "missing_house_appliance_files": dataset["missing_files"],
            "small_files": dataset["small_files"],
            "train_rows": len(dataset["y_train"]),
            "validation_rows": len(dataset["y_validation"]),
            "train_class_counts": {
                CLASSES[index]: int(np.sum(dataset["y_train"] == index))
                for index in range(4)
            },
            "validation_class_counts": {
                CLASSES[index]: int(np.sum(dataset["y_validation"] == index))
                for index in range(4)
            },
            "train_row_ids_sha256": sha256_text(train_row_ids),
            "validation_row_ids_sha256": sha256_text(validation_row_ids),
            "same_rows_and_labels_for_both_encodings": True,
            "raw_features_all_finite": True,
        },
        "encoding_fits": fits,
        "checks": {
            "both_encodings_train_shape": [
                int(encoded["han_binary"][0].shape[0]),
                int(encoded["han_binary"][0].shape[1]),
            ],
            "both_encodings_validation_shape": [
                int(encoded["threshold_8"][1].shape[0]),
                int(encoded["threshold_8"][1].shape[1]),
            ],
            "both_exactly_184_bits": True,
            "threshold_fit_from_training_only": True,
            "no_nan_or_infinity": True,
            "paired_initial_model_states": True,
            "fixed_seed_reproducibility": reproducibility,
        },
        "summaries": {
            "han_binary": metric_summary(rows, "han_binary"),
            "threshold_8": metric_summary(rows, "threshold_8"),
        },
        "paired_macro_f1": {
            "threshold_minus_han_by_seed": {
                str(seed): delta for seed, delta in zip(SEEDS, deltas)
            },
            "mean": mean_delta,
            "sample_std": statistics.stdev(deltas),
            "wins": wins,
            "losses": losses,
            "ties": ties,
        },
        "decision_rule_result": decision,
        "limitations": [
            "Exploratory scratch result only; not formal model selection.",
            "Does not modify Protocol R or final classes.",
            "Uses legacy label-assisted matched events rather than raw-time Protocol R events.",
            "H2 and H4 were sealed and not read.",
            "Does not test TMU or compare TM trainers.",
            "Does not run firmware, Pico, Arduino, model export, or deployment.",
            "The encodings trade maximum per-feature resolution (256 versus 9 levels) as well as structure.",
        ],
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    hb = summary["summaries"]["han_binary"]
    th = summary["summaries"]["threshold_8"]
    seed_lines = []
    for seed in SEEDS:
        h = by_encoding_seed[("han_binary", seed)]
        t = by_encoding_seed[("threshold_8", seed)]
        seed_lines.append(
            f"| {seed} | {h['macro_f1']:.6f} | {t['macro_f1']:.6f} | "
            f"{t['macro_f1'] - h['macro_f1']:+.6f} |"
        )
    file_lines = [
        f"| H{item['house']} | {item['appliance']} | {item['events']} | "
        f"{item['train_events']} | {item['validation_events']} |"
        for item in dataset["files"]
    ]
    feature_lines = "\n".join(
        f"{index}. `{feature}`" for index, feature in enumerate(FEATURES, 1)
    )
    report = f"""# E001 Booleanization A/B Probe

**Status:** Complete\\
**Decision:** **{decision}**\\
**Scope:** Exploratory scratch probe only; not formal model selection, T004, a protocol change, or final thesis evidence.

## Data boundary

Only existing matched-transition CSVs for H1, H3, H5, and H6 were read. H2 and H4 remained sealed and were not read. Files were stably sorted by `start`; files with at least five events used the first floor(80%) for training and the remainder for validation.

| House | Appliance | Events | Train | Validation |
|---|---|---:|---:|---:|
{chr(10).join(file_lines)}

The H5 microwave file contained one event and was retained entirely in training. Training contains {len(dataset['y_train'])} rows and validation contains {len(dataset['y_validation'])} rows. Validation contains all four classes.

## Encoding comparison

`han_binary` exactly uses Han's training-set mean/std, standardisation, Gaussian CDF, and ordinary 8-bit binary representation. It can represent at most 256 levels per feature.

`threshold_8` fits q = 1/9 through 8/9 empirical quantiles from training rows only, using NumPy's deterministic `linear` quantile method, and emits `value >= threshold` bits. It can represent at most 9 levels per feature. Repeated thresholds and bits are retained.

Both use 23 × 8 = 184 bits. This is therefore an overall comparison of numerical resolution and monotonic structure under the same bit budget, not merely a bit reordering.

## Ordered feature slots

{feature_lines}

The duplicate `duration` slots 2 and 7 are retained.

## Fixed TM contract

- Han Tsetlin implementation at `{HAN_ROOT}`
- Four classes in the fixed requested order
- 200 clauses, 50 states, T=20, s=6.0
- 10 epochs
- Seeds 0–4
- One unique full training-event shuffle per epoch
- No balancing, hard negatives, Drop Clause, multigranular s, or hyperparameter search

## Results

| Encoding | Accuracy mean ± sample SD | Macro F1 mean ± sample SD | Training seconds mean ± sample SD |
|---|---:|---:|---:|
| han_binary | {hb['accuracy']['mean']:.6f} ± {hb['accuracy']['sample_std']:.6f} | {hb['macro_f1']['mean']:.6f} ± {hb['macro_f1']['sample_std']:.6f} | {hb['training_seconds']['mean']:.3f} ± {hb['training_seconds']['sample_std']:.3f} |
| threshold_8 | {th['accuracy']['mean']:.6f} ± {th['accuracy']['sample_std']:.6f} | {th['macro_f1']['mean']:.6f} ± {th['macro_f1']['sample_std']:.6f} | {th['training_seconds']['mean']:.3f} ± {th['training_seconds']['sample_std']:.3f} |

| Seed | han_binary Macro F1 | threshold_8 Macro F1 | Paired delta |
|---:|---:|---:|---:|
{chr(10).join(seed_lines)}

Mean paired Macro-F1 delta: **{mean_delta:+.6f}**.\\
Wins/losses/ties for threshold_8: **{wins}/{losses}/{ties}**.

The promising rule requires a mean improvement of at least 0.02 and wins in at least 4 of 5 seeds. Result: **{decision}**.

Per-class F1 values, confusion matrices, training times, model-state hashes, fitted parameters, file hashes, and sample standard deviations are in `per_seed_metrics.csv` and `summary.json`.

## Checks

- Both encodings used identical training/validation rows and labels.
- Both emitted exactly 184 bits with only 0/1 values.
- All fitted parameters used training rows only.
- Raw and encoded values contained no NaN or infinity.
- Paired encodings used identical initial model state for each seed.
- Repeating seed 0 reproduced predictions, metrics, and final model state for both encodings.

## Limitations

This uses legacy label-assisted matched-event data and is not Protocol R. It does not test TMU, another trainer, model export, firmware, Pico, Arduino, deployment, causal aggregate-only inference, or real-time behaviour. No result here changes the approved research protocol or formal class decision.
"""
    (OUTPUT_ROOT / "REPORT.md").write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "complete",
                "decision": decision,
                "train_rows": len(dataset["y_train"]),
                "validation_rows": len(dataset["y_validation"]),
                "han_macro_f1": hb["macro_f1"],
                "threshold_macro_f1": th["macro_f1"],
                "paired_delta": summary["paired_macro_f1"],
                "reproducibility": reproducibility,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
