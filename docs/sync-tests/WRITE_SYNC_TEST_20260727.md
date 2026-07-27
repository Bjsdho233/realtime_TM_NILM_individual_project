# GitHub Write-Sync Test — 2026-07-27

Test ID: `WS-20260727-01`

## Purpose

This temporary file is a real repository write used to verify that fresh Codex and
ChatGPT conversations can discover the same unmerged GitHub state, distinguish it
from the canonical published state, and later recover the merged state from
`main`.

## Required interpretation while this PR is open

- Canonical published state remains the GitHub default branch `main`.
- This branch and its Draft PR are in-flight test state only.
- This test does not activate or authorise any T-series, E-series, or R-series work.
- T004 remains planned and not authorised.
- No experiment, training, prediction, REDD access, Protocol R decision, evidence
  promotion, or Pico work is part of this test.
- No project result, protocol, evaluation rule, or claim boundary is changed.

## Expected zero-context observation

A fresh agent inspecting GitHub should report:

1. `main` still points to the pre-test canonical state until the PR is merged.
2. The Draft PR exists and contains this file.
3. Test ID `WS-20260727-01` is visible only in the in-flight branch/PR.
4. The Draft PR must not be treated as canonical research state.

## Lifecycle

After both fresh-agent reads succeed, this Draft PR may be merged to test
default-branch synchronization. A separate cleanup PR may then delete this file.
Git history and the PR timeline remain the audit trail that the test actually
occurred.
