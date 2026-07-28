from __future__ import annotations

import unittest

import numpy as np

from tools.baseline.encoding import GaussianCdfEncoder
from tools.baseline.model import BinaryTsetlinMachine, ModelConfig


class DeterministicBinaryTmTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(17)
        self.x = rng.integers(0, 2, size=(12, 184), dtype=np.uint8)
        self.y = np.asarray([0, 1] * 6, dtype=np.uint8)

    def test_seed_controls_initialisation_shuffle_and_training(self) -> None:
        first = BinaryTsetlinMachine(seed=3)
        second = BinaryTsetlinMachine(seed=3)
        first_orders = first.fit(self.x, self.y, epochs=2)
        second_orders = second.fit(self.x, self.y, epochs=2)
        self.assertEqual(first_orders, second_orders)
        self.assertEqual(first.to_training_bytes(), second.to_training_bytes())
        self.assertEqual(first.to_inference_bytes(), second.to_inference_bytes())
        self.assertTrue(
            np.array_equal(first.predict(self.x)[0], second.predict(self.x)[0])
        )

    def test_initial_state_actions_are_consistent(self) -> None:
        model = BinaryTsetlinMachine(seed=0)
        self.assertTrue(model.state_action_consistent())
        positive, negative = model.action_masks()
        self.assertTrue(np.logical_xor(positive, negative).all())

    def test_signed_vote_uses_strict_positive_and_zero_tie_is_negative(self) -> None:
        config = ModelConfig(n_features=4, n_clauses=4)
        model = BinaryTsetlinMachine(seed=0, config=config)
        model.states.fill(model.middle_state)
        x = np.asarray([1, 0, 1, 0], dtype=np.uint8)
        self.assertEqual(model.class_votes_one(x), (0, 0))
        self.assertEqual(model.signed_vote_one(x), 0)
        self.assertEqual(model.predict_one(x), 0)

        # Make every positive clause of class 0 contradictory.
        model.states[0, 0, :, 0, 0] = model.middle_state + 1
        model.states[0, 0, :, 1, 0] = model.middle_state + 1
        self.assertGreater(model.signed_vote_one(x), 0)
        self.assertEqual(model.predict_one(x), 1)

    def test_training_and_inference_reload_preserve_votes_and_predictions(self) -> None:
        model = BinaryTsetlinMachine(seed=4)
        model.fit(self.x, self.y, epochs=2)
        expected_predictions, expected_votes = model.predict(self.x)
        training_reload = BinaryTsetlinMachine.from_training_bytes(
            model.to_training_bytes()
        )
        inference_reload = BinaryTsetlinMachine.from_inference_bytes(
            model.to_inference_bytes(), seed=4
        )
        for reloaded in (training_reload, inference_reload):
            predictions, votes = reloaded.predict(self.x)
            self.assertTrue(np.array_equal(expected_predictions, predictions))
            self.assertTrue(np.array_equal(expected_votes, votes))

    def test_every_constructor_call_returns_fresh_state_storage(self) -> None:
        first = BinaryTsetlinMachine(seed=1)
        second = BinaryTsetlinMachine(seed=1)
        self.assertIsNot(first, second)
        self.assertFalse(np.shares_memory(first.states, second.states))
        first.states[0, 0, 0, 0, 0] = 1
        self.assertNotEqual(first.states[0, 0, 0, 0, 0], second.states[0, 0, 0, 0, 0])


class EncoderTests(unittest.TestCase):
    def test_encoder_fits_training_only_and_does_not_mutate_inputs(self) -> None:
        training = np.arange(92, dtype=np.float64).reshape(4, 23)
        validation = np.full((2, 23), 1000.0, dtype=np.float64)
        training_copy = training.copy()
        validation_copy = validation.copy()
        encoder = GaussianCdfEncoder.fit(
            training, feature_schema_sha256="a" * 64
        )
        state_before = encoder.serialize()
        encoded_training = encoder.transform(training)
        encoded_validation = encoder.transform(validation)
        self.assertTrue(np.array_equal(training, training_copy))
        self.assertTrue(np.array_equal(validation, validation_copy))
        self.assertEqual(state_before, encoder.serialize())
        self.assertTrue(np.array_equal(encoder.mean, np.mean(training, axis=0)))
        self.assertEqual(encoded_training.shape, (4, 184))
        self.assertEqual(encoded_validation.shape, (2, 184))

    def test_zero_standard_deviation_maps_to_standardised_zero(self) -> None:
        training = np.ones((3, 23), dtype=np.float64)
        encoder = GaussianCdfEncoder.fit(training, feature_schema_sha256="b" * 64)
        encoded = encoder.transform(np.full((1, 23), 99.0))
        self.assertEqual(encoded.shape, (1, 184))
        self.assertTrue(np.array_equal(encoded[0, :8], encoded[0, 8:16]))


if __name__ == "__main__":
    unittest.main()

