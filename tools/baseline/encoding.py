"""Han-compatible training-only Gaussian-CDF Booleanisation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _han_erf(values: np.ndarray) -> np.ndarray:
    """Vectorised Abramowitz-Stegun 7.1.26 used by the pinned Han source."""

    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    signs = np.where(values >= 0.0, 1.0, -1.0)
    absolute = np.abs(values)
    t = 1.0 / (1.0 + p * absolute)
    polynomial = (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1)
    return signs * (1.0 - polynomial * t * np.exp(-(absolute * absolute)))


@dataclass(frozen=True)
class GaussianCdfEncoder:
    mean: np.ndarray
    std: np.ndarray
    feature_schema_sha256: str
    training_candidate_count: int

    @classmethod
    def fit(
        cls,
        features: np.ndarray,
        *,
        feature_schema_sha256: str,
    ) -> "GaussianCdfEncoder":
        source = np.asarray(features, dtype=np.float64)
        if source.ndim != 2 or source.shape[1] != 23:
            raise ValueError("encoder training features must have shape (n, 23)")
        if source.shape[0] == 0 or not np.isfinite(source).all():
            raise ValueError("encoder training features must be non-empty and finite")
        return cls(
            mean=np.mean(source, axis=0, dtype=np.float64),
            std=np.std(source, axis=0, dtype=np.float64),
            feature_schema_sha256=feature_schema_sha256,
            training_candidate_count=int(source.shape[0]),
        )

    def transform(self, features: np.ndarray) -> np.ndarray:
        source = np.asarray(features, dtype=np.float64)
        if source.ndim != 2 or source.shape[1] != 23:
            raise ValueError("encoder input must have shape (n, 23)")
        if not np.isfinite(source).all():
            raise ValueError("encoder input contains non-finite values")
        safe_std = np.where(self.std == 0.0, 1.0, self.std)
        standardised = (source.copy() - self.mean) / safe_std
        standardised[:, self.std == 0.0] = 0.0
        cdf = 0.5 * (1.0 + _han_erf(standardised / np.sqrt(2.0)))
        quantised = np.rint(np.clip(cdf, 0.0, 1.0) * 255.0).astype(np.uint8)
        shifts = np.arange(7, -1, -1, dtype=np.uint8)
        encoded = ((quantised[:, :, None] >> shifts) & 1).reshape(
            source.shape[0], 184
        )
        return encoded.astype(np.uint8, copy=False)

    def state_record(self) -> dict[str, object]:
        return {
            "schema_version": "t005-gaussian-cdf-8bit-v1",
            "feature_schema_sha256": self.feature_schema_sha256,
            "fit_scope": "fold training aggregate-main candidates only",
            "training_candidate_count": self.training_candidate_count,
            "mean": self.mean.tolist(),
            "std": self.std.tolist(),
            "zero_std_policy": "standardised value zero",
            "cdf": "Han Abramowitz-Stegun 7.1.26 approximation",
            "quantisation": "round-to-even over 0..255",
            "bit_order": "MSB-first",
            "numeric_slots": 23,
            "boolean_inputs": 184,
        }

    def serialize(self) -> bytes:
        return canonical_json_bytes(self.state_record())

    def sha256(self) -> str:
        return hashlib.sha256(self.serialize()).hexdigest()

