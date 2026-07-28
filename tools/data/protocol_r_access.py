#!/usr/bin/env python3
"""Fail-closed development access for the frozen T004 Protocol R manifest."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


MANIFEST_RELATIVE_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.json")
HASH_RELATIVE_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.sha256")
FROZEN_MANIFEST_SHA256 = "501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5"
ALLOWED_ROLES = {"training", "validation"}
DENIED_ROLE_ALIASES = {
    "b5",
    "locked",
    "locked_test",
    "test",
    "protocol_x",
    "candidate_test",
}
PROTOCOL_R_HOUSES = {1, 3, 5, 6}
DENIED_HOUSES = {2, 4}


class ProtocolRAccessDenied(PermissionError):
    """Raised when ordinary development requests protected data."""


class ProtocolRManifestError(RuntimeError):
    """Raised when the frozen manifest or its source identity is invalid."""


@dataclass(frozen=True)
class DevelopmentSlice:
    source_relative_path: str
    source_sha256: str
    house: int
    segment_id: str
    block_id: str
    row_start_inclusive: int
    row_end_exclusive: int
    valid_target_start_inclusive: int
    valid_target_end_exclusive: int
    fold_id: str
    role: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_frozen_manifest(project_root: Path) -> dict[str, object]:
    root = project_root.resolve()
    manifest_path = root / MANIFEST_RELATIVE_PATH
    hash_path = root / HASH_RELATIVE_PATH
    if not manifest_path.is_file() or not hash_path.is_file():
        raise ProtocolRManifestError("the frozen T004 manifest and hash sidecar are required")

    digest = sha256_file(manifest_path)
    if digest != FROZEN_MANIFEST_SHA256:
        raise ProtocolRManifestError("the frozen T004 manifest byte hash does not match")
    expected_sidecar = (
        f"{FROZEN_MANIFEST_SHA256}  {MANIFEST_RELATIVE_PATH.as_posix()}\n"
    )
    if hash_path.read_text(encoding="ascii") != expected_sidecar:
        raise ProtocolRManifestError("the frozen T004 manifest hash sidecar does not match")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_id") != "t004-protocol-r-evaluation-v1":
        raise ProtocolRManifestError("unexpected evaluation manifest identity")
    if manifest.get("manifest_status") != "frozen evaluation contract; B5 locked until T011":
        raise ProtocolRManifestError("evaluation manifest is not frozen")
    access = manifest.get("access_contract")
    if not isinstance(access, dict) or access.get("ordinary_entry_has_locked_test_switch") is not False:
        raise ProtocolRManifestError("manifest does not define a fail-closed ordinary entry")
    return manifest


def _normalise_role(role: str) -> str:
    normalised = role.strip().lower().replace("-", "_")
    if normalised in DENIED_ROLE_ALIASES:
        raise ProtocolRAccessDenied(
            f"development access explicitly denies protected role: {role}"
        )
    if normalised not in ALLOWED_ROLES:
        raise ProtocolRAccessDenied(
            f"development role must be one of {sorted(ALLOWED_ROLES)}"
        )
    return normalised


def _normalise_fold(validation_fold: int) -> str:
    if isinstance(validation_fold, bool) or validation_fold not in range(1, 5):
        raise ValueError("validation_fold must be an integer from 1 through 4")
    return f"F{validation_fold}"


def development_slices(
    project_root: Path,
    *,
    validation_fold: int,
    role: str,
    houses: tuple[int, ...] | None = None,
) -> tuple[DevelopmentSlice, ...]:
    """Return only B1-B4 slices admitted for one fixed development fold."""

    manifest = _load_frozen_manifest(project_root)
    fold_id = _normalise_fold(validation_fold)
    normalised_role = _normalise_role(role)

    requested_houses = set(houses) if houses is not None else set(PROTOCOL_R_HOUSES)
    if requested_houses & DENIED_HOUSES:
        denied = sorted(requested_houses & DENIED_HOUSES)
        raise ProtocolRAccessDenied(
            f"Protocol X houses are unavailable to Protocol R development: {denied}"
        )
    if not requested_houses or not requested_houses <= PROTOCOL_R_HOUSES:
        raise ProtocolRAccessDenied("requested houses are outside the Protocol R population")

    fold = next(
        item
        for item in manifest["protocol_r"]["blocked_cv"]
        if item["fold_id"] == fold_id
    )
    admitted_blocks = (
        set(fold["training_blocks"])
        if normalised_role == "training"
        else {fold["validation_block"]}
    )
    if "B5" in admitted_blocks:
        raise ProtocolRManifestError("development fold unexpectedly admits B5")

    slices = []
    for source in manifest["source_files"]:
        house = source["house"]
        if house not in requested_houses:
            continue
        if source["protocol_role"] != "protocol_r_population":
            raise ProtocolRManifestError("Protocol X source entered Protocol R development")
        for block in source["blocks"]:
            if block["block_id"] not in admitted_blocks:
                continue
            if block["role"] != "development":
                raise ProtocolRManifestError("protected block entered Protocol R development")
            valid = block["valid_target_range"]
            slices.append(
                DevelopmentSlice(
                    source_relative_path=source["relative_path"],
                    source_sha256=source["sha256"],
                    house=house,
                    segment_id=source["segment_id"],
                    block_id=block["block_id"],
                    row_start_inclusive=block["row_start_inclusive"],
                    row_end_exclusive=block["row_end_exclusive"],
                    valid_target_start_inclusive=valid["row_start_inclusive"],
                    valid_target_end_exclusive=valid["row_end_exclusive"],
                    fold_id=fold_id,
                    role=normalised_role,
                )
            )
    if not slices:
        raise ProtocolRManifestError("development request produced no admitted slices")
    return tuple(slices)


def iter_development_rows(
    project_root: Path,
    redd_root: Path,
    *,
    validation_fold: int,
    role: str,
    houses: tuple[int, ...] | None = None,
) -> Iterator[tuple[DevelopmentSlice, int, dict[str, str]]]:
    """Yield admitted CSV rows without exposing a protected-role switch."""

    root = redd_root.resolve()
    for data_slice in development_slices(
        project_root,
        validation_fold=validation_fold,
        role=role,
        houses=houses,
    ):
        source_path = root / Path(data_slice.source_relative_path).name
        if not source_path.is_file():
            raise ProtocolRManifestError(
                f"admitted source is unavailable: {data_slice.source_relative_path}"
            )
        if sha256_file(source_path) != data_slice.source_sha256:
            raise ProtocolRManifestError(
                f"admitted source fingerprint changed: {data_slice.source_relative_path}"
            )
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_position, row in enumerate(reader):
                if row_position < data_slice.row_start_inclusive:
                    continue
                if row_position >= data_slice.row_end_exclusive:
                    break
                yield data_slice, row_position, row
