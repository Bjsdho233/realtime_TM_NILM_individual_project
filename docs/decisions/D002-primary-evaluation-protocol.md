# D002 — Primary Evaluation Protocol

**Status:** Accepted\
**Date:** 2026-07-21\
**Decision owner:** Tianhang Tan\
**Decision scope:** Evaluation framework only; the concrete data split remains `Pending`.

## Context

The project has two different purposes:

1. reproduce a minimum Han-compatible training-to-Pico workflow;
2. conduct controlled research experiments under a leakage-controlled evaluation protocol.

These purposes must not share the same evidential status. A successful compatibility reproduction proves that the engineering path works, but it does not by itself establish the project's research performance.

The previous project used several exploratory data arrangements. Those historical results remain useful evidence, but they were not produced under the protocol defined here and therefore cannot be reported as results from the new project's primary evaluation.

## Decision

The project will use four named protocols:

| Protocol | Purpose | Evidential status |
|---|---|---|
| Protocol H | Han-compatible workflow reproduction and engineering validation. | Compatibility evidence only. |
| Protocol R | Main mixed-house, raw-time blocked research evaluation. | Primary dissertation result. |
| Protocol X | Optional held-out-house stress test. | Additional generalisation evidence only. |
| Protocol D | Final deployment-model training after method freeze. | Deployment evidence only. |

Protocol R is the primary research protocol.

## Protocol H

Protocol H is used to establish the minimum engineering path:

`local training -> model export -> Python verification -> host-native verification -> Pico inference`

It may follow a pinned revision of Han's workflow where useful, but exact file-for-file reproduction is not required.

Protocol H must record material differences in:

- data preparation;
- appliance classes;
- feature order;
- preprocessing;
- Booleanisation;
- TM structure and parameters;
- model export;
- embedded behaviour.

Protocol H results must not be presented as Protocol R research results.

Protocol H must not use the future Protocol R candidate test block for training, method selection, or compatibility scoring.

The exact Protocol H data, configuration, and reference revision remain `Pending`.

## Protocol R

Protocol R is a mixed-house, raw-time blocked evaluation.

Each eligible REDD house must be treated as an independent continuous recording before its processed events are combined with events from other houses.

The following rules apply:

- Split each house in raw time before event detection, event pairing, feature extraction, or Booleanisation.
- Do not concatenate signals from different houses into an artificial continuous time series.
- Reset detector, pairer, feature, and other causal state at every house boundary.
- Reset the same state at every split boundary.
- Fit normalisation, Booleanisation thresholds, duration limits, and other learned preprocessing using training data only.
- Use validation data for development, parameter selection, error analysis, and method selection.
- Keep the frozen test unavailable during development.
- Keep aggregate-mains-only inference separate from label-assisted or oracle analysis.
- Record the source house, time range, split identity, and processing configuration for every formal event set.

After independent per-house processing, eligible training events may be pooled across houses. The same applies separately to validation and test events.

The exact houses, appliance classes, split ratios, time boundaries, and purge remain `Pending`.

## Candidate Test and Freeze Process

Protocol R uses three stages.

### 1. Preflight

Before the split is frozen, a proposed future-test region is called the `candidate test block`.

Preflight may inspect only:

- available houses and channels;
- timestamp coverage;
- recording gaps;
- label-derived appliance support;
- whether the proposed blocks are technically evaluable.

Preflight must not use:

- model scores;
- classification errors;
- feature quality;
- hyperparameter comparisons;
- experiment outcomes from the candidate test block.

All information inspected during preflight must be recorded.

### 2. Freeze

The candidate test block becomes the `locked test` only after Tianhang approves:

- the eligible houses;
- the appliance class set;
- the raw-time boundaries;
- the split proportions;
- the purge rule;
- the split manifest;
- the manifest identity or hash.

Until that approval, the term `locked test` must not be used.

### 3. Final Evaluation

After the freeze:

- training and development code must not access the locked test;
- method selection must use training and validation evidence only;
- the final method, configuration, code revision, models, and metrics must be declared before test access;
- final test results must not be used to choose between configurations;
- final test results must not trigger further tuning presented as untouched-test development.

The final evaluation must be performed through a separately approved named task.

## Protocol X

Protocol X may hold out one or more complete houses to examine cross-house generalisation.

It is optional and is not the primary success criterion of this project.

Its execution, held-out houses, appliance support requirements, and acceptance criteria remain `Pending`.

Protocol X should be considered only after the main Protocol R method has been selected and evaluated.

## Protocol D

Protocol D is used to produce the final deployment model after the research method has been frozen and the Protocol R final evaluation has been completed.

It may use a broader approved training set than Protocol R.

Protocol D may be used for:

- final model export;
- Pico parity verification;
- firmware resource measurement;
- latency measurement;
- causal replay demonstration.

Protocol D results must not be presented as unbiased Protocol R test results.

## Primary Metrics

The primary Protocol R classification metric is macro F1 over the frozen appliance class set.

Formal reports must also include:

- per-class precision, recall, F1, and support;
- macro precision and recall;
- accuracy;
- confusion matrix;
- number of houses;
- time coverage;
- event count;
- input and ground-truth definitions.

The final appliance class set and exact acceptance criteria remain `Pending`.

Label-assisted event, pairing, or classification measurements must be identified explicitly as label-assisted or oracle evidence.

## Pending Protocol Inputs

The following items must be resolved through named tasks:

- local REDD path;
- available houses and channels;
- timestamp coverage and recording gaps;
- appliance class set;
- split proportions;
- raw-time boundaries;
- purge rule;
- minimum class-support requirements;
- Protocol H data and configuration;
- Protocol X execution and held-out houses;
- repeated-run and seed policy;
- final evaluation manifest.

Historical experiments must not be used silently to fill these fields.

## Consequences

### Positive consequences

- Compatibility reproduction is separated from formal research evaluation.
- Test feedback cannot guide ordinary model development.
- Events near house and split boundaries cannot inherit hidden state from another partition.
- Training-only preprocessing reduces leakage risk.
- Mixed-house performance and held-out-house generalisation are reported as different questions.
- Deployment results remain clearly distinguishable from unbiased research results.

### Costs and limitations

- Raw recordings must be inventoried before the split can be approved.
- Event data cannot be generated once and then divided arbitrarily.
- Some historical results will need to be reproduced before they can support the new project.
- The locked test cannot be used for iterative debugging or model selection.
- Protocol X may be infeasible if complete held-out houses do not support the frozen class set.

## Actions Not Authorised by This Decision

This decision does not itself authorise:

- accessing or processing REDD;
- choosing houses, classes, boundaries, ratios, or purge;
- generating the split manifest;
- training or evaluating a model;
- importing algorithm code;
- compiling or flashing firmware;
- initialising Git;
- creating commits, remotes, or GitHub repositories.

Those actions require separate named tasks and explicit approval.
