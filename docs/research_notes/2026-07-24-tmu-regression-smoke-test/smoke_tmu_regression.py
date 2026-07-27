from __future__ import annotations

import inspect
import platform
import sys
from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np


@dataclass
class ModelResult:
    name: str
    weighted_clauses: bool
    fit_success: bool
    predict_success: bool
    prediction_shape: tuple[int, ...] | None
    prediction_min: float | None
    prediction_max: float | None
    all_finite: bool
    unique_predictions: int | None
    test_mae: float | None
    mean_baseline_mae: float
    fit_seconds: float
    predict_seconds: float
    error: str | None


def make_synthetic_regression() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20260724)
    x = rng.uniform(-2.0, 2.0, size=(160, 3))
    y = (
        12.0
        + 4.0 * x[:, 0]
        - 2.5 * x[:, 1]
        + 1.75 * x[:, 2]
        + 0.8 * x[:, 0] * x[:, 2]
    )
    return x, y


def run_model(
    *,
    name: str,
    weighted_clauses: bool,
    model_type,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
) -> ModelResult:
    baseline_mae = float(np.mean(np.abs(y_test - np.mean(y_train))))
    fit_seconds = 0.0
    predict_seconds = 0.0

    try:
        model = model_type(
            number_of_clauses=64,
            T=40,
            s=3.0,
            platform="CPU",
            max_included_literals=16,
            weighted_clauses=weighted_clauses,
            seed=20260724,
        )

        fit_start = perf_counter()
        for _ in range(3):
            model.fit(x_train, y_train, shuffle=True)
        fit_seconds = perf_counter() - fit_start

        predict_start = perf_counter()
        prediction = np.asarray(model.predict(x_test))
        predict_seconds = perf_counter() - predict_start

        all_finite = bool(np.isfinite(prediction).all())
        shape_ok = prediction.shape == y_test.shape

        return ModelResult(
            name=name,
            weighted_clauses=weighted_clauses,
            fit_success=True,
            predict_success=True,
            prediction_shape=prediction.shape,
            prediction_min=float(np.min(prediction)),
            prediction_max=float(np.max(prediction)),
            all_finite=all_finite,
            unique_predictions=int(np.unique(prediction).size),
            test_mae=float(np.mean(np.abs(prediction - y_test))),
            mean_baseline_mae=baseline_mae,
            fit_seconds=fit_seconds,
            predict_seconds=predict_seconds,
            error=None if shape_ok else f"Expected prediction shape {y_test.shape}, got {prediction.shape}",
        )
    except Exception as exc:
        return ModelResult(
            name=name,
            weighted_clauses=weighted_clauses,
            fit_success=fit_seconds > 0.0,
            predict_success=False,
            prediction_shape=None,
            prediction_min=None,
            prediction_max=None,
            all_finite=False,
            unique_predictions=None,
            test_mae=None,
            mean_baseline_mae=baseline_mae,
            fit_seconds=fit_seconds,
            predict_seconds=predict_seconds,
            error=f"{type(exc).__name__}: {exc}",
        )


def main() -> int:
    started = perf_counter()

    try:
        from tmu.models.regression.vanilla_regressor import TMRegressor
        from tmu.preprocessing.standard_binarizer.binarizer import StandardBinarizer
    except Exception as exc:
        print(f"IMPORT_SUCCESS=False")
        print(f"IMPORT_ERROR={type(exc).__name__}: {exc}")
        return 1

    print("IMPORT_SUCCESS=True")
    print(f"PYTHON={sys.version.split()[0]}")
    print(f"ARCHITECTURE={platform.architecture()[0]}")
    print(f"TMREGRESSOR_SIGNATURE={inspect.signature(TMRegressor)}")

    x, y = make_synthetic_regression()
    split_rng = np.random.default_rng(311)
    indices = split_rng.permutation(x.shape[0])
    train_indices = indices[:120]
    test_indices = indices[120:]

    x_train_continuous = x[train_indices]
    x_test_continuous = x[test_indices]
    y_train = y[train_indices]
    y_test = y[test_indices]

    binarizer = StandardBinarizer(max_bits_per_feature=8)
    x_train = binarizer.fit_transform(x_train_continuous).astype(np.uint32)
    x_test = binarizer.transform(x_test_continuous).astype(np.uint32)

    print("BOOLEANISATION_SUCCESS=True")
    print(f"BOOLEANISED_TRAIN_SHAPE={x_train.shape}")
    print(f"BOOLEANISED_TEST_SHAPE={x_test.shape}")
    print(f"BOOLEANISED_TRAIN_DTYPE={x_train.dtype}")
    print(f"BOOLEANISED_TEST_DTYPE={x_test.dtype}")
    print(f"TRAIN_TARGET_RANGE=({float(np.min(y_train)):.12f}, {float(np.max(y_train)):.12f})")
    print(f"TRAIN_TARGET_UNIQUE={int(np.unique(y_train).size)}")

    results = [
        run_model(
            name="vanilla_rtm",
            weighted_clauses=False,
            model_type=TMRegressor,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        ),
        run_model(
            name="weighted_rtm",
            weighted_clauses=True,
            model_type=TMRegressor,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        ),
    ]

    for result in results:
        print(f"{result.name.upper()}={asdict(result)}")

    passed = all(
        result.fit_success
        and result.predict_success
        and result.prediction_shape == y_test.shape
        and result.all_finite
        and result.error is None
        for result in results
    )
    print(f"TOTAL_RUNTIME_SECONDS={perf_counter() - started:.6f}")
    print("WARNING=PyCUDA is intentionally absent; TMU may log a CUDA import warning before using CPU.")
    print(f"SMOKE_TEST_RESULT={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
