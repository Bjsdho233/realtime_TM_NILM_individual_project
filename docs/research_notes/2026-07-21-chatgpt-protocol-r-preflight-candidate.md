# Supplementary Research Note — ChatGPT Protocol R Candidate V4

**Status:** Superseded candidate; not an active protocol, decision, or verified project result

**Analysis date:** 2026-07-21

**Source:** Web ChatGPT-side exploratory preflight

**Canonical replacement:** T002, D003, D004, and `protocol_r_approved_split.json`

## Purpose of this record

This note preserves an independently developed Protocol R candidate that was produced before the desktop Codex T002 audit became the canonical project evidence. It is retained because the support analysis and rejected design choices may help explain later protocol decisions.

The analysis ran in a separate ChatGPT/Codex container rather than Tianhang's authoritative local project. Under the repository evidence rules, its execution claims and generated counts are supplementary research notes, not locally verified project results.

This record must not change `docs/CURRENT_STATE.md`, reopen T002, replace the approved split, or be used to select a model.

## Candidate that was analysed

The exploratory candidate proposed:

- source: 35 preprocessed synchronized REDD CSV segments, treated as independent sequences;
- selected houses: H1, H2, and H3;
- classes: `fridge`, `microwave`, and `dish washer`;
- split within every segment: 40% train, 20% validation, and 40% candidate test;
- state reset at every segment and split boundary;
- boundary exclusion: 532 samples on each side, derived from a 500-sample Han pairing bound plus 32 samples of episode context;
- relative row position as the sequence coordinate because the supplied CSVs did not contain original timestamps.

The original draft called the final 40% a locked test. That terminology was premature because Tianhang had not approved or frozen the candidate. This record therefore uses **candidate test**.

## Label-assisted support probe

The probe used appliance labels only. It did not run aggregate-mains event detection, event pairing, feature extraction, TM training, or model scoring.

Its exploratory rules were:

- active threshold: power greater than 15 W;
- significant edge threshold: 80 W;
- candidate-pair upper bound: structural rise/fall opportunity count, not accepted pairs;
- draft adequacy target: at least 60 candidate-pair opportunities and contributions from at least two houses for every class and split.

The reported global upper bounds were:

| Split | Fridge | Microwave | Dish washer |
|---|---:|---:|---:|
| Train | 471 | 141 | 75* |
| Validation | 197 | 68 | 65 |
| Candidate test | 446 | 102 | 89 |

These values are feasibility-only oracle statistics. They are not event counts, classifier support, or performance metrics. In particular, validation dish-washer support was highly concentrated: H1 contributed 64 of the 65 reported opportunities, H2 contributed 0, and H3 contributed 1. Passing the draft two-house rule therefore did not imply balanced cross-house support.

\* Import validation found that the train/dish-washer global report was 75 while its per-house values were 43, 22, and 9, which sum to 74. The other eight global values equal their per-house sums. Both values are preserved in the structured record rather than silently corrected. This one-count discrepancy indicates an unresolved boundary or roll-up defect in the exploratory analysis, so the reported global counts must not be reused as canonical evidence.

The exploratory inventory reported 35 files, six houses, and 1,508,578 rows. Its legacy aggregate identifier was `0b7e12b5f42db36d83d958fb2cd3b0d8ae5074d19fde49852c9c04d7ed40833a`. That identifier used the exploratory preflight's own serialization and must not be substituted for the canonical T002 content-tree fingerprint.

## Why this candidate was superseded

The later desktop Codex T002 process established a different, reviewed contract:

- H1, H3, H5, and H6 form the train/validation pool;
- H2 and H4 form the sealed candidate test;
- validation uses three contiguous row-position blocks per segment;
- boundary safety uses full dependency containment rather than an assumed fixed 532-sample purge;
- the approved four-class set is `fridge`, `microwave`, `dish washer`, and `washer dryer`;
- absent label columns remain an evaluation-policy question and are not silently treated as appliance absence;
- support thresholds and the optional class fallback were declared and reviewed through D003 and D004.

The exploratory candidate is therefore not a competing active configuration. It captures an earlier line of reasoning that prioritised complete three-class label availability in every selected house. The canonical T002 contract instead preserves a broader four-class research target, separates development houses from sealed candidate-test houses, and records missing-label handling as a decision that must be resolved before evaluation.

## Permitted use

This note may be used to:

- reconstruct the history of Protocol R design;
- explain why support totals alone are insufficient without per-house concentration checks;
- compare fixed numerical purge assumptions with full dependency containment;
- motivate the distinction between an exploratory candidate and an approved protocol.

It must not be used as:

- the Protocol R split manifest;
- an approved class or house decision;
- evidence that the candidate test was locked;
- a source of dissertation performance numbers;
- permission to access H2/H4 model outputs or begin model execution.

## Structured companion and current authority

The structured companion record is:

- `artifacts/manifests/chatgpt_protocol_r_preflight_candidate_v4.json`

Current project authority remains with:

- `docs/decisions/D003-redd-sequence-time-contract.md`;
- `docs/decisions/D004-protocol-r-class-fallback.md`;
- `artifacts/manifests/protocol_r_approved_split.json`;
- `docs/data/PROTOCOL_R_PREFLIGHT.md`;
- `docs/CURRENT_STATE.md`.
