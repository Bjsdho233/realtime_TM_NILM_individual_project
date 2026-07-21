# T003 Han Source Audit

**Date:** 2026-07-21\
**Task:** T003 — Han reference audit and minimum reproduction contract\
**Status:** In progress

## Work completed

- Reconfirmed the clean research repository, fixed Han `main` commit `8c5e90df34236ba0afcc4ec46ac083d829de4d51`, matching `origin/main`, and clean REDD submodule commit `a621bbd6399e49c6798550618fe43b113149455b`.
- Performed a static-only audit of the root Python entries, TM implementation and compiler, protobuf schema, Arduino examples/runtime, POSIX prototype, dependency declarations, README commands, website data references, and UK-DALE notebook structure.
- Recorded the evidence in [`HAN_PIPELINE_SOURCE_AUDIT.md`](../reproduction/HAN_PIPELINE_SOURCE_AUDIT.md) and the machine-readable [`han_pipeline_source_inventory.json`](../../artifacts/manifests/han_pipeline_source_inventory.json).
- Distinguished wired/reachable code, implementation without demonstrated reachability, documented claims, and unresolved evidence.
- Reconciled the active feature dimensions as 23 ordered numeric slots, 22 unique names, 184 Boolean TM inputs, and 368 possible positive/negated literals per clause.
- Recorded that no unique canonical entry point can be proved and that the staged, integrated Python, Arduino, and POSIX paths materially differ.
- Recorded unresolved model provenance, generated-header placement, missing build inputs/headers, Python/firmware Booleanisation parity, and exact board/toolchain information.
- Recorded that the integrated ESP32 sketch replays native float samples from SD and reads post-event samples from that file; it is not evidence of live causal NILM.
- Compared the Han snapshot with the approved Protocol R manifest without changing D003, D004, T002 evidence, or any Protocol R manifest.

## Boundaries observed

- No Han Python, notebook, shell, Arduino, or POSIX program was executed.
- No dependency was installed and no environment was changed.
- No edge detection, event pairing, feature extraction, training, inference, scoring, benchmark, or compilation was run.
- No upstream or REDD submodule file was modified.
- No upstream source or data was copied into the research repository.
- No network, fetch, pull, checkout, reset, or submodule update occurred.
- No T004 or later task, Pico work, firmware implementation, or hardware work began.

## Current disposition

The static source-audit phase is complete, but T003 remains **In progress**. No reusable component, canonical compatibility entry, model bundle, or minimum reproduction contract is approved by this record. The next action is Tianhang/ChatGPT review and a separate explicit decision on the executable reproduction boundary.
