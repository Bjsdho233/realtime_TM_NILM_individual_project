"""Deterministic project-owned repair of the pinned Han binary TM."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

import numpy as np


INFERENCE_MAGIC = b"T5BI"
TRAINING_MAGIC = b"T5BT"
FORMAT_VERSION = 1


@dataclass(frozen=True)
class ModelConfig:
    n_features: int = 184
    n_classes: int = 2
    n_clauses: int = 200
    n_states: int = 50
    T: int = 20
    s: float = 6.0


class BinaryTsetlinMachine:
    """Han learning rule with consistent initial actions and one seeded RNG."""

    def __init__(self, *, seed: int, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        if self.config.n_classes != 2:
            raise ValueError("T005 requires exactly two classes")
        if self.config.n_clauses % 2 or self.config.n_states % 2:
            raise ValueError("clause and automaton state counts must be even")
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        half = self.config.n_clauses // 2
        middle = self.config.n_states // 2
        choices = self.rng.integers(
            0,
            2,
            size=(self.config.n_classes, 2, half, self.config.n_features),
            dtype=np.int16,
        )
        self.states = np.empty(
            (self.config.n_classes, 2, half, 2, self.config.n_features),
            dtype=np.int16,
        )
        self.states[:, :, :, 0, :] = middle + choices
        self.states[:, :, :, 1, :] = middle + (1 - choices)

    @property
    def middle_state(self) -> int:
        return self.config.n_states // 2

    def action_masks(self) -> tuple[np.ndarray, np.ndarray]:
        return (
            self.states[:, :, :, 0, :] > self.middle_state,
            self.states[:, :, :, 1, :] > self.middle_state,
        )

    def state_action_consistent(self) -> bool:
        positive, negative = self.action_masks()
        return bool(
            np.array_equal(positive, self.states[:, :, :, 0, :] > self.middle_state)
            and np.array_equal(
                negative, self.states[:, :, :, 1, :] > self.middle_state
            )
        )

    def _clause_outputs(self, class_id: int, polarity: int, x: np.ndarray) -> np.ndarray:
        clause_states = self.states[class_id, polarity]
        included_positive = clause_states[:, 0, :] > self.middle_state
        included_negative = clause_states[:, 1, :] > self.middle_state
        positive_ok = np.all(~included_positive | x[None, :], axis=1)
        negative_ok = np.all(~included_negative | (~x)[None, :], axis=1)
        return (positive_ok & negative_ok).astype(np.int8)

    def class_votes_one(self, encoded: np.ndarray) -> tuple[int, int]:
        x = np.asarray(encoded, dtype=np.uint8).astype(bool, copy=False)
        if x.shape != (self.config.n_features,):
            raise ValueError("encoded sample has an unexpected shape")
        votes = []
        for class_id in range(2):
            positive = self._clause_outputs(class_id, 0, x)
            negative = self._clause_outputs(class_id, 1, x)
            votes.append(int(np.sum(positive) - np.sum(negative)))
        return votes[0], votes[1]

    def signed_vote_one(self, encoded: np.ndarray) -> int:
        negative_vote, positive_vote = self.class_votes_one(encoded)
        return positive_vote - negative_vote

    def predict_one(self, encoded: np.ndarray) -> int:
        return int(self.signed_vote_one(encoded) > 0)

    def predict(self, encoded: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        matrix = np.asarray(encoded, dtype=np.uint8)
        predictions = np.empty(matrix.shape[0], dtype=np.uint8)
        signed_votes = np.empty(matrix.shape[0], dtype=np.int32)
        for index, sample in enumerate(matrix):
            signed_vote = self.signed_vote_one(sample)
            signed_votes[index] = signed_vote
            predictions[index] = int(signed_vote > 0)
        return predictions, signed_votes

    def _type_i(
        self,
        class_id: int,
        polarity: int,
        clause_index: int,
        x: np.ndarray,
        clause_output: int,
    ) -> None:
        states = self.states[class_id, polarity, clause_index]
        positive = states[0]
        negative = states[1]
        s1 = 1.0 / self.config.s
        s2 = (self.config.s - 1.0) / self.config.s
        if clause_output == 0:
            positive_mask = (positive > 1) & (
                self.rng.random(self.config.n_features) <= s1
            )
            negative_mask = (negative > 1) & (
                self.rng.random(self.config.n_features) <= s1
            )
            positive[positive_mask] -= 1
            negative[negative_mask] -= 1
            return

        positive_random = self.rng.random(self.config.n_features)
        positive[(x & (positive < self.config.n_states) & (positive_random <= s2))] += 1
        positive[
            ((~x) & (positive > 1) & (positive_random <= s1))
        ] -= 1
        negative_random = self.rng.random(self.config.n_features)
        negative[
            (x & (negative > 1) & (negative_random <= s1))
        ] -= 1
        negative[
            ((~x) & (negative < self.config.n_states) & (negative_random <= s2))
        ] += 1

    def _type_ii(
        self,
        class_id: int,
        polarity: int,
        clause_index: int,
        x: np.ndarray,
    ) -> None:
        states = self.states[class_id, polarity, clause_index]
        positive = states[0]
        negative = states[1]
        positive[((~x) & (positive <= self.middle_state))] += 1
        negative[(x & (negative <= self.middle_state))] += 1

    def step(self, encoded: np.ndarray, target: int) -> None:
        x = np.asarray(encoded, dtype=np.uint8).astype(bool, copy=False)
        target = int(target)
        if target not in (0, 1):
            raise ValueError("binary target must be 0 or 1")
        other = 1 - target
        target_positive = self._clause_outputs(target, 0, x)
        target_negative = self._clause_outputs(target, 1, x)
        target_sum = int(
            np.clip(
                int(np.sum(target_positive) - np.sum(target_negative)),
                -self.config.T,
                self.config.T,
            )
        )
        target_probability = (self.config.T - target_sum) / (2 * self.config.T)
        for clause_index in range(self.config.n_clauses // 2):
            if self.rng.random() <= target_probability:
                self._type_i(target, 0, clause_index, x, int(target_positive[clause_index]))
            if (
                target_negative[clause_index] == 1
                and self.rng.random() <= target_probability
            ):
                self._type_ii(target, 1, clause_index, x)

        other_positive = self._clause_outputs(other, 0, x)
        other_negative = self._clause_outputs(other, 1, x)
        other_sum = int(
            np.clip(
                int(np.sum(other_positive) - np.sum(other_negative)),
                -self.config.T,
                self.config.T,
            )
        )
        other_probability = (self.config.T + other_sum) / (2 * self.config.T)
        for clause_index in range(self.config.n_clauses // 2):
            if other_positive[clause_index] == 1 and self.rng.random() <= other_probability:
                self._type_ii(other, 0, clause_index, x)
            if self.rng.random() <= other_probability:
                self._type_i(other, 1, clause_index, x, int(other_negative[clause_index]))

    def fit(
        self,
        encoded: np.ndarray,
        targets: np.ndarray,
        *,
        epochs: int = 10,
        shuffle_seed: int | None = None,
    ) -> list[str]:
        matrix = np.asarray(encoded, dtype=np.uint8)
        labels = np.asarray(targets, dtype=np.uint8)
        if matrix.ndim != 2 or matrix.shape[1] != self.config.n_features:
            raise ValueError("training matrix has an unexpected shape")
        if labels.shape != (matrix.shape[0],) or not np.isin(labels, [0, 1]).all():
            raise ValueError("training labels must be a binary vector")
        shuffle_rng = np.random.default_rng(
            self.seed if shuffle_seed is None else int(shuffle_seed)
        )
        order_hashes = []
        for _ in range(int(epochs)):
            order = shuffle_rng.permutation(matrix.shape[0])
            if np.unique(order).size != matrix.shape[0]:
                raise RuntimeError("epoch order is not a unique permutation")
            order_hashes.append(hashlib.sha256(order.astype("<i8").tobytes()).hexdigest())
            for index in order:
                self.step(matrix[int(index)], int(labels[int(index)]))
        return order_hashes

    def to_training_bytes(self) -> bytes:
        header = struct.pack(
            "<4sH5Hq",
            TRAINING_MAGIC,
            FORMAT_VERSION,
            self.config.n_features,
            self.config.n_classes,
            self.config.n_clauses,
            self.config.n_states,
            self.config.T,
            self.seed,
        )
        return header + self.states.astype("<i2", copy=False).tobytes(order="C")

    @classmethod
    def from_training_bytes(
        cls, payload: bytes, *, s: float = 6.0
    ) -> "BinaryTsetlinMachine":
        header_size = struct.calcsize("<4sH5Hq")
        magic, version, n_features, n_classes, n_clauses, n_states, T, seed = (
            struct.unpack("<4sH5Hq", payload[:header_size])
        )
        if magic != TRAINING_MAGIC or version != FORMAT_VERSION:
            raise ValueError("unexpected training model format")
        config = ModelConfig(n_features, n_classes, n_clauses, n_states, T, s)
        model = cls(seed=seed, config=config)
        expected_shape = (n_classes, 2, n_clauses // 2, 2, n_features)
        states = np.frombuffer(payload[header_size:], dtype="<i2")
        if states.size != int(np.prod(expected_shape)):
            raise ValueError("training model state length mismatch")
        model.states = states.reshape(expected_shape).astype(np.int16, copy=True)
        return model

    def to_inference_bytes(self) -> bytes:
        header = struct.pack(
            "<4sH5H",
            INFERENCE_MAGIC,
            FORMAT_VERSION,
            self.config.n_features,
            self.config.n_classes,
            self.config.n_clauses,
            self.config.n_states,
            self.config.T,
        )
        records = bytearray()
        included_positive, included_negative = self.action_masks()
        for class_id in range(self.config.n_classes):
            for polarity in range(2):
                for clause_index in range(self.config.n_clauses // 2):
                    positive_positions = np.flatnonzero(
                        included_positive[class_id, polarity, clause_index]
                    )
                    negative_positions = np.flatnonzero(
                        included_negative[class_id, polarity, clause_index]
                    )
                    records.extend(
                        struct.pack("<HH", len(positive_positions), len(negative_positions))
                    )
                    for position in positive_positions:
                        records.extend(struct.pack("<H", int(position)))
                    for position in negative_positions:
                        records.extend(struct.pack("<H", int(position)))
        return header + bytes(records)

    @classmethod
    def from_inference_bytes(
        cls, payload: bytes, *, seed: int = 0, s: float = 6.0
    ) -> "BinaryTsetlinMachine":
        header_size = struct.calcsize("<4sH5H")
        magic, version, n_features, n_classes, n_clauses, n_states, T = struct.unpack(
            "<4sH5H", payload[:header_size]
        )
        if magic != INFERENCE_MAGIC or version != FORMAT_VERSION:
            raise ValueError("unexpected inference model format")
        config = ModelConfig(n_features, n_classes, n_clauses, n_states, T, s)
        model = cls(seed=seed, config=config)
        model.states.fill(model.middle_state)
        cursor = header_size
        for class_id in range(n_classes):
            for polarity in range(2):
                for clause_index in range(n_clauses // 2):
                    if cursor + 4 > len(payload):
                        raise ValueError("truncated inference clause")
                    n_positive, n_negative = struct.unpack("<HH", payload[cursor : cursor + 4])
                    cursor += 4
                    for literal_polarity, count in ((0, n_positive), (1, n_negative)):
                        byte_count = 2 * count
                        if cursor + byte_count > len(payload):
                            raise ValueError("truncated inference literal positions")
                        positions = np.frombuffer(
                            payload[cursor : cursor + byte_count], dtype="<u2"
                        )
                        cursor += byte_count
                        if np.any(positions >= n_features):
                            raise ValueError("inference literal position out of range")
                        model.states[
                            class_id, polarity, clause_index, literal_polarity, positions
                        ] = model.middle_state + 1
        if cursor != len(payload):
            raise ValueError("trailing inference model bytes")
        return model

    def inference_sha256(self) -> str:
        return hashlib.sha256(self.to_inference_bytes()).hexdigest()
