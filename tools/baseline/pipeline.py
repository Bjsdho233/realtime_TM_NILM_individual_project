"""Aggregate-main candidate construction and post-construction target association."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np

from tools.data.protocol_r_access import DevelopmentSlice


APPLIANCES = ("fridge", "microwave", "dish washer")
FEATURE_NAMES = (
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
)


@dataclass(frozen=True)
class CandidateEvent:
    candidate_id: str
    house: int
    segment_id: str
    block_id: str
    rise_row: int
    fall_row: int
    dependency_start_row: int
    dependency_end_row: int
    available_row: int
    features: tuple[float, ...]

    @property
    def onset_to_output_samples(self) -> int:
        return self.available_row - self.rise_row


@dataclass(frozen=True)
class TargetEpisode:
    episode_id: str
    start_row: int
    end_row: int


@dataclass
class TargetAssociation:
    label_available: bool
    candidate_status: dict[str, int | None]
    candidate_exclusion_reason: dict[str, str]
    matched_candidate_to_episode: dict[str, str]
    matched_episode_to_candidate: dict[str, str]
    complete_episode_count: int
    unmatched_complete_episode_count: int
    duplicate_candidate_ids: set[str]
    excluded_counts: Counter[str]


@dataclass
class BlockResult:
    data_slice: DevelopmentSlice
    candidates: list[CandidateEvent]
    associations: dict[str, TargetAssociation]
    diagnostics: Counter[str]


def feature_schema_record() -> dict[str, object]:
    formulas = (
        ("transition", "W", "rise delta"),
        ("duration", "samples", "fall row minus rise row"),
        ("pos_transition_magnitude", "W", "rise delta"),
        ("neg_transition_magnitude", "W", "absolute falling delta"),
        ("abs_transition", "W", "0.5 * (positive magnitude + negative magnitude)"),
        ("log_abs_transition", "log1p(W)", "log1p(abs_transition)"),
        ("duration", "samples", "fall row minus rise row; intentional duplicate"),
        ("log_duration", "log1p(samples)", "log1p(duration)"),
        (
            "transition_duration_product",
            "W*sample proxy",
            "abs_transition * max(1, duration)",
        ),
        (
            "transition_duration_ratio",
            "W/sample proxy",
            "abs_transition / max(1, duration)",
        ),
        ("episode_mean_main", "W", "mean(main[rise:fall inclusive])"),
        ("episode_std_main", "W", "population std(main[rise:fall inclusive])"),
        ("episode_min_main", "W", "minimum(main[rise:fall inclusive])"),
        ("episode_max_main", "W", "maximum(main[rise:fall inclusive])"),
        ("episode_range_main", "W", "episode maximum minus minimum"),
        (
            "internal_diff_mean_abs",
            "W",
            "mean absolute first difference within episode",
        ),
        (
            "internal_diff_max_abs",
            "W",
            "maximum absolute first difference within episode",
        ),
        (
            "internal_edge_count",
            "count",
            "internal absolute differences >= max(1 W, 0.25*abs_transition)",
        ),
        (
            "subcycle_count_proxy",
            "count proxy",
            "max(0, internal_edge_count - 1)",
        ),
        (
            "active_fraction_proxy",
            "fraction proxy",
            "fraction episode >= minimum + 0.25*range when range > 0",
        ),
        (
            "episode_energy_estimate",
            "W-sample proxy",
            "sum(max(episode - pre-window mean, 0))",
        ),
        (
            "post_minus_pre_mean",
            "W",
            "mean(8 post-fall samples) - mean(32 pre-rise samples)",
        ),
        (
            "event_internal_edge_count",
            "count",
            "count abs(diff with first prepended) >= 50 W",
        ),
    )
    slots = []
    for index, (name, unit, formula) in enumerate(formulas, start=1):
        slots.append(
            {
                "slot": index,
                "name": name,
                "unit": unit,
                "formula": formula,
                "dtype": "float64",
            }
        )
    return {
        "schema_version": "t005-aggregate-main-23slot-v1",
        "source_reference": (
            "wuhanstudio/nilm@8c5e90df34236ba0afcc4ec46ac083d829de4d51 "
            "redd_event_pair.py episode_feature_row; required formulas only"
        ),
        "ordered_slots": slots,
        "intentional_duplicate": "duration appears at slots 2 and 7",
        "missing_policy": "exclude candidate if any dependency value is non-finite",
        "dependency_interval": "rise-32 through fall+8 inclusive",
        "available_time": "fall+8",
        "history_samples_maximum": 256,
        "post_context_samples": 8,
    }


def feature_schema_bytes() -> bytes:
    return (
        json.dumps(
            feature_schema_record(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def feature_schema_sha256() -> str:
    return hashlib.sha256(feature_schema_bytes()).hexdigest()


def _parse_number(raw: str | None) -> float:
    if raw is None or raw.strip() == "":
        return math.nan
    try:
        return float(raw)
    except ValueError:
        return math.nan


def rows_to_arrays(
    rows: Iterable[Mapping[str, str]],
) -> tuple[np.ndarray, dict[str, np.ndarray | None]]:
    materialised = list(rows)
    main = np.asarray([_parse_number(row.get("main")) for row in materialised])
    targets: dict[str, np.ndarray | None] = {}
    for appliance in APPLIANCES:
        if materialised and appliance in materialised[0]:
            targets[appliance] = np.asarray(
                [_parse_number(row.get(appliance)) for row in materialised],
                dtype=np.float64,
            )
        else:
            targets[appliance] = None
    return main, targets


def _candidate_features(
    main: np.ndarray,
    *,
    rise_index: int,
    fall_index: int,
    positive_delta: float,
    negative_delta: float,
) -> tuple[float, ...]:
    pre = main[rise_index - 32 : rise_index]
    episode = main[rise_index : fall_index + 1]
    post = main[fall_index + 1 : fall_index + 9]
    dependency = main[rise_index - 32 : fall_index + 9]
    if (
        len(pre) != 32
        or len(post) != 8
        or len(episode) == 0
        or not np.isfinite(dependency).all()
    ):
        raise ValueError("candidate feature dependency is incomplete or non-finite")

    duration = float(fall_index - rise_index)
    positive_magnitude = float(positive_delta)
    negative_magnitude = float(abs(negative_delta))
    absolute_transition = 0.5 * (positive_magnitude + negative_magnitude)
    episode_mean = float(np.mean(episode))
    episode_std = float(np.std(episode))
    episode_min = float(np.min(episode))
    episode_max = float(np.max(episode))
    episode_range = episode_max - episode_min
    differences = np.abs(np.diff(episode))
    edge_threshold = max(1.0, 0.25 * absolute_transition)
    internal_edge_count = int(np.sum(differences >= edge_threshold))
    active_fraction = (
        float(np.mean(episode >= (episode_min + 0.25 * episode_range)))
        if episode_range > 0
        else 0.0
    )
    baseline = float(np.mean(pre))
    prepended_delta = np.diff(episode, prepend=episode[0])
    values = (
        positive_magnitude,
        duration,
        positive_magnitude,
        negative_magnitude,
        absolute_transition,
        math.log1p(absolute_transition),
        duration,
        math.log1p(duration),
        absolute_transition * max(1.0, duration),
        absolute_transition / max(1.0, duration),
        episode_mean,
        episode_std,
        episode_min,
        episode_max,
        episode_range,
        float(np.mean(differences)) if len(differences) else 0.0,
        float(np.max(differences)) if len(differences) else 0.0,
        float(internal_edge_count),
        float(max(0, internal_edge_count - 1)),
        active_fraction,
        float(np.sum(np.maximum(episode - baseline, 0.0))),
        float(np.mean(post) - np.mean(pre)),
        float(np.count_nonzero(np.abs(prepended_delta) >= 50.0)),
    )
    if len(values) != 23 or not np.isfinite(values).all():
        raise ValueError("candidate features are not finite 23-slot values")
    return tuple(float(value) for value in values)


def build_main_candidates(
    data_slice: DevelopmentSlice, main: np.ndarray
) -> tuple[list[CandidateEvent], Counter[str]]:
    diagnostics: Counter[str] = Counter()
    candidates: list[CandidateEvent] = []
    rises: deque[tuple[int, float]] = deque()
    previous = math.nan
    block_start = data_slice.row_start_inclusive
    for local_index, value in enumerate(np.asarray(main, dtype=np.float64)):
        global_row = block_start + local_index
        while rises and local_index - rises[0][0] > 223:
            rises.popleft()
            diagnostics["expired_rise_count"] += 1
        if not math.isfinite(float(value)):
            diagnostics["non_finite_main_count"] += 1
            diagnostics["expired_rise_count"] += len(rises)
            rises.clear()
            previous = math.nan
            continue
        if not math.isfinite(previous):
            previous = float(value)
            continue
        delta = float(value) - previous
        previous = float(value)
        if delta >= 50.0:
            diagnostics["rising_edge_count"] += 1
            rises.append((local_index, delta))
            continue
        if delta > -50.0:
            continue
        diagnostics["falling_edge_count"] += 1
        if not rises:
            diagnostics["unmatched_fall_count"] += 1
            continue
        rise_index, positive_delta = rises.popleft()
        diagnostics["paired_count"] += 1
        dependency_start = rise_index - 32
        dependency_end = local_index + 8
        fall_inside_valid_target = (
            data_slice.valid_target_start_inclusive
            <= global_row
            < data_slice.valid_target_end_exclusive
        )
        if (
            dependency_start < 0
            or dependency_end >= len(main)
            or not fall_inside_valid_target
        ):
            diagnostics["contained_candidate_exclusion_count"] += 1
            continue
        dependency = main[dependency_start : dependency_end + 1]
        if len(dependency) > 264:
            raise RuntimeError("candidate dependency exceeds 256 history plus 8 post samples")
        if not np.isfinite(dependency).all():
            diagnostics["non_finite_candidate_exclusion_count"] += 1
            continue
        features = _candidate_features(
            main,
            rise_index=rise_index,
            fall_index=local_index,
            positive_delta=positive_delta,
            negative_delta=delta,
        )
        rise_row = block_start + rise_index
        candidate_id = (
            f"H{data_slice.house}|{data_slice.segment_id}|{data_slice.block_id}|"
            f"R{rise_row}|F{global_row}"
        )
        candidates.append(
            CandidateEvent(
                candidate_id=candidate_id,
                house=data_slice.house,
                segment_id=data_slice.segment_id,
                block_id=data_slice.block_id,
                rise_row=rise_row,
                fall_row=global_row,
                dependency_start_row=block_start + dependency_start,
                dependency_end_row=block_start + dependency_end,
                available_row=global_row + 8,
                features=features,
            )
        )
    diagnostics["expired_rise_count"] += len(rises)
    diagnostics["candidate_count"] = len(candidates)
    diagnostics["main_edge_count"] = (
        diagnostics["rising_edge_count"] + diagnostics["falling_edge_count"]
    )
    return candidates, diagnostics


def _target_episodes(
    values: np.ndarray,
    *,
    block_start: int,
    appliance: str,
    segment_id: str,
    block_id: str,
) -> tuple[list[TargetEpisode], list[tuple[int, int, str]], Counter[str]]:
    complete: list[TargetEpisode] = []
    ambiguous: list[tuple[int, int, str]] = []
    counts: Counter[str] = Counter()
    finite = np.isfinite(values)
    active = finite & (values > 15.0)
    index = 0
    while index < len(values):
        if not active[index]:
            if not finite[index]:
                start = index
                while index + 1 < len(values) and not finite[index + 1]:
                    index += 1
                ambiguous.append((block_start + start, block_start + index, "non_finite_target"))
                counts["non_finite_target_run_count"] += 1
            index += 1
            continue
        start = index
        while index + 1 < len(values) and active[index + 1]:
            index += 1
        end = index
        length = end - start + 1
        reason = None
        if length < 2:
            reason = "incomplete_one_sample"
        elif start == 0:
            reason = "left_censored"
        elif end == len(values) - 1:
            reason = "right_censored"
        elif not finite[start - 1] or not finite[end + 1]:
            reason = "non_finite_boundary"
        if reason is not None:
            ambiguous.append((block_start + start, block_start + end, reason))
            counts[f"{reason}_episode_count"] += 1
        else:
            start_row = block_start + start
            end_row = block_start + end
            episode_id = (
                f"{appliance}|{segment_id}|{block_id}|T{start_row}-{end_row}"
            )
            complete.append(TargetEpisode(episode_id, start_row, end_row))
        index += 1
    counts["complete_episode_count"] = len(complete)
    return complete, ambiguous, counts


def associate_targets(
    candidates: list[CandidateEvent],
    target_values: np.ndarray | None,
    *,
    data_slice: DevelopmentSlice,
    appliance: str,
) -> TargetAssociation:
    if target_values is None:
        return TargetAssociation(
            label_available=False,
            candidate_status={candidate.candidate_id: None for candidate in candidates},
            candidate_exclusion_reason={
                candidate.candidate_id: "label_unavailable" for candidate in candidates
            },
            matched_candidate_to_episode={},
            matched_episode_to_candidate={},
            complete_episode_count=0,
            unmatched_complete_episode_count=0,
            duplicate_candidate_ids=set(),
            excluded_counts=Counter({"label_unavailable": len(candidates)}),
        )

    complete, ambiguous, counts = _target_episodes(
        target_values,
        block_start=data_slice.row_start_inclusive,
        appliance=appliance,
        segment_id=data_slice.segment_id,
        block_id=data_slice.block_id,
    )
    status: dict[str, int | None] = {}
    exclusion_reason: dict[str, str] = {}
    eligible_candidates = []
    for candidate in candidates:
        intersecting_reasons = sorted(
            {
                reason
                for start, end, reason in ambiguous
                if candidate.rise_row <= end and candidate.fall_row >= start
            }
        )
        if intersecting_reasons:
            reason = "+".join(intersecting_reasons)
            status[candidate.candidate_id] = None
            exclusion_reason[candidate.candidate_id] = reason
            counts[f"ambiguous_candidate_{reason}"] += 1
        else:
            eligible_candidates.append(candidate)

    pairs = []
    admissible_by_candidate: dict[str, set[str]] = {}
    for candidate in eligible_candidates:
        for episode in complete:
            if (
                candidate.rise_row - 2 <= episode.end_row + 2
                and candidate.fall_row + 2 >= episode.start_row - 2
            ):
                real_overlap = max(
                    0,
                    min(candidate.fall_row, episode.end_row)
                    - max(candidate.rise_row, episode.start_row)
                    + 1,
                )
                boundary_error = abs(candidate.rise_row - episode.start_row) + abs(
                    candidate.fall_row - episode.end_row
                )
                pairs.append(
                    (
                        -real_overlap,
                        boundary_error,
                        candidate.candidate_id,
                        episode.episode_id,
                    )
                )
                admissible_by_candidate.setdefault(candidate.candidate_id, set()).add(
                    episode.episode_id
                )
    pairs.sort()
    matched_candidates: dict[str, str] = {}
    matched_episodes: dict[str, str] = {}
    for _negative_overlap, _boundary_error, candidate_id, episode_id in pairs:
        if candidate_id in matched_candidates or episode_id in matched_episodes:
            continue
        matched_candidates[candidate_id] = episode_id
        matched_episodes[episode_id] = candidate_id

    duplicate_ids = set()
    for candidate in eligible_candidates:
        candidate_id = candidate.candidate_id
        if candidate_id in matched_candidates:
            status[candidate_id] = 1
            continue
        status[candidate_id] = 0
        if any(
            episode_id in matched_episodes
            for episode_id in admissible_by_candidate.get(candidate_id, set())
        ):
            duplicate_ids.add(candidate_id)

    unmatched = len(complete) - len(matched_episodes)
    counts["matched_target_episode_count"] = len(matched_episodes)
    counts["unmatched_target_episode_count"] = unmatched
    counts["duplicate_candidate_count"] = len(duplicate_ids)
    return TargetAssociation(
        label_available=True,
        candidate_status=status,
        candidate_exclusion_reason=exclusion_reason,
        matched_candidate_to_episode=matched_candidates,
        matched_episode_to_candidate=matched_episodes,
        complete_episode_count=len(complete),
        unmatched_complete_episode_count=unmatched,
        duplicate_candidate_ids=duplicate_ids,
        excluded_counts=counts,
    )


def process_block(
    data_slice: DevelopmentSlice, rows: Iterable[Mapping[str, str]]
) -> BlockResult:
    main, targets = rows_to_arrays(rows)
    expected_length = data_slice.row_end_exclusive - data_slice.row_start_inclusive
    if len(main) != expected_length:
        raise RuntimeError("access layer returned an incomplete block")
    candidates, diagnostics = build_main_candidates(data_slice, main)
    associations = {
        appliance: associate_targets(
            candidates,
            targets[appliance],
            data_slice=data_slice,
            appliance=appliance,
        )
        for appliance in APPLIANCES
    }
    return BlockResult(data_slice, candidates, associations, diagnostics)


def candidate_identity_sha256(candidates: Iterable[CandidateEvent]) -> str:
    digest = hashlib.sha256()
    for candidate in candidates:
        digest.update(candidate.candidate_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(np.asarray(candidate.features, dtype="<f8").tobytes())
    return digest.hexdigest()

