# Agent Guidance

## Scope and Authority

This file contains stable repository-wide rules. Current phase, active work,
temporary permissions, and next actions belong only in
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

- Tianhang owns formal research decisions, test access, publication, destructive
  actions, external writes, and material scope changes.
- A current, explicit instruction from Tianhang can authorise scoped work. Live
  authority and active status are recorded only in `docs/CURRENT_STATE.md`; work
  records preserve scope and evidence but are not a second authority registry.
  When a clear instruction starts new work, registering it there is the first
  action, not a reason to stop.
- Accepted decisions are not silently overridden by an implementation assumption.
- Direct governance maintenance requested by Tianhang may update governance files
  without creating a research task ID. It cannot alter an accepted protocol
  decision without a corresponding decision record.
- Once a T/E/R or governance scope is authorised, creating new task-scoped files
  inside its authorised mutable/output boundary does not require a second
  permission. This includes new source, configuration, tests, documents, research
  notes, review reports, manifests, run/debug records, aggregate tables or figures,
  progress records, and the exact lifecycle/index rows required by this file.
- This record-first authority does not permit an unrequested change to existing
  shared code, protocols, accepted decisions, or historical conclusions. An
  instruction that explicitly requests such a change is the confirmation for that
  named scope; do not ask again for every file edit. Live status/index maintenance
  and append-only experiment logs remain permitted within the authorised work.
- New records preserve context; they do not by themselves approve a method,
  promote exploratory evidence, change the formal baseline, or establish a
  dissertation claim.
- Conversation summaries and reported results are context, not local execution
  evidence. The inspected worktree and locally verified outputs are authoritative.
- Preserve historical records as historical records; correct them through a
  current-state update or supersession note.

## Research Method Authority and Source Attribution

Tianhang is accountable for the dissertation and owns its research methods.
Codex may decide how to implement an accepted method, but it must not decide what
the research method should be. Keep method selection and implementation work
explicitly separate.

Codex may autonomously perform `Implementation-only` work that preserves the
accepted algorithmic meaning and evidence population, including:

- file structure, CLI design and configuration plumbing;
- data readers, caching, batching, vectorisation and implementation-level
  performance optimisation;
- logging, plotting and result export;
- unit tests, boundary checks and failure diagnostics;
- code refactoring that does not alter the method;
- implementation of an already accepted or frozen model specification.

The following are research-method choices and require Tianhang's explicit review
and confirmation before implementation or evidence-producing execution:

- what constitutes one sample;
- input-window length, causality and permitted delay;
- raw power, differences, statistics, event features or another representation;
- Booleanisation method, threshold generation and bits per feature;
- target definition, transformation and scaling;
- cTM, rTM, weighted rTM or a combined structure;
- treatment of OFF-sample imbalance;
- data splits, evaluation metrics and post-processing;
- tunable parameters, search space and selection rule;
- dissertation contribution, originality and novelty framing.

If an authorised coding task encounters an unresolved method choice, stop before
implementing or running that choice. Present the options, sources, consequences
and the smallest decision Tianhang must make. A convenient implementation
assumption, library default or prototype setting is not method approval.
Implementation optimisation must not silently change samples, features,
thresholds, targets, splits, model semantics, metrics or claims.

Every method component and material run configuration must identify one of these
source types in the applicable task, design, review or report before it produces
evidence:

| Source type | Meaning | Required dissertation treatment |
|---|---|---|
| `Inherited` | Directly uses an existing paper or code method. | Cite the exact reference, implementation and version. |
| `Adapted` | Modifies or applies an existing method for this project. | Cite the original method and state the project modification separately. |
| `Project-designed` | Chosen by this project from a stated hypothesis or design need. | Record motivation, alternatives considered and the decision process. |
| `Implementation-only` | Changes code or execution mechanics without changing algorithmic meaning. | Describe only to the extent needed for reproducibility and engineering explanation. |

An absent source is not evidence of novelty. Treat an unsourced project choice as
`Project-designed`, not as an innovation or original contribution. Novelty may be
discussed only after an adequate literature review and Tianhang's explicit
approval of that claim. Do not describe a mixed method as a single “standard”
method: separate inherited model mechanics and library components from adapted
task formulation, project-designed inputs/configuration and implementation-only
engineering.

Prototype parameters such as window length, lag representation, bits per
feature, row caps, epochs and clause counts are not literature-backed or optimal
merely because they appear in an authorised run specification. Authorisation
permits the declared run; it does not promote those choices into the final method
or a dissertation contribution.

## Prototype-First Dissertation Scope

This repository is a student individual-project prototype, not a
production-delivery programme. Future work must optimise for a runnable,
readable and honestly explainable dissertation system.

- Make claim-critical questions credible, make secondary questions
  explainable, and document then defer frontier problems once their boundary is
  clear.
- Prefer the smallest end-to-end implementation that supports the main
  dissertation line. Every new abstraction, layer, experiment family, schema,
  validator or infrastructure component needs a named claim, safety boundary or
  demonstrable implementation need. Otherwise omit or defer it.
- Keep architecture, code paths, configuration and reports compact enough for
  Tianhang to run and explain. Do not pursue production-grade completeness,
  exhaustive edge-case coverage, enterprise deployment machinery or speculative
  extensibility.
- Verification is proportional: protect data leakage and accepted evaluation
  boundaries, test the main runnable path and material failure modes, and avoid
  large test matrices for low-consequence details.
- T004/T005 remain valid historical records, but their governance and evidence
  weight is not the default template for later work. Do not expand or rework
  them merely to simplify their history.
- Do not turn an optional theoretical concern into a blocker unless it can
  invalidate the main result, make the claim dishonest, expose protected data or
  prevent the prototype from running.

For real-time claims, a prototype is sufficient when it consumes data in time
order, does not revise an emitted decision using later whole-segment knowledge,
and has a fixed, disclosed and acceptable processing/algorithmic delay. Depending
on the demonstrated boundary, honest terms include `real-time replay`,
`bounded-delay streaming inference`, and `real-time-capable inference`. Bit-level
parity, zero latency and placing every pipeline stage on hardware are not default
requirements. State the measured and algorithmic delay and the exact host/device
boundary instead.

## Starting Work

For a fresh or context-free session, follow
[`START_HERE.md`](START_HERE.md) before modifying anything. At minimum:

1. inspect the actual worktree and Git state;
2. read `docs/CURRENT_STATE.md`, `docs/WORK_INDEX.md`, applicable decisions, and
   the relevant work record;
3. run `python scripts/check_repo.py` from the repository root;
4. report any contradiction between the worktree, default branch, and status
   documents before continuing;
5. classify the request as T-series, E-series, R-series review, or the direct
   governance-maintenance exception defined above;
6. confirm its data, evidence, output, and external-action boundary;
7. preserve unrelated and user-owned changes;
8. perform the smallest useful unit, verify it, and report changed files,
   commands, checks, failures, and material checks not run.

A test command that discovers zero tests is a failure, not a successful check.

Do not stop merely because the full roadmap is unfinished or an unrelated formal
choice is `Pending`. Stop when a missing choice would:

- expose sealed candidate-test or locked-test information;
- create leakage or change the evaluation population;
- alter an accepted protocol, metric, class set, or formal claim;
- modify shared state outside the authorised track;
- require destructive work, external writes, credentials, hardware, or material
  scope expansion;
- make the result impossible to interpret honestly.

An E-series may use a provisional assumption when it is experiment-local,
recorded before execution, and cannot change formal project state.

## Work Tracks

Titles, index/status rows, and the first reference in a document must use an ID
with a direct name, such as
`T003 — Han Two-Class PC Reproduction` or
`E001 — Booleanisation Encoding A/B Probe`. The short ID may be used after it has
been defined in the same context; a bare number must not be the only identity.

| Track | Authorisation and permitted work | Boundary |
|---|---|---|
| T-series | Tianhang explicitly authorises formal engineering, protocol, baseline, evaluation, or deployment work. A new formal specification normally belongs at `docs/tasks/T###-direct-name.md`; a completed inherited task may instead point to its durable result record. | May change shared project state. Completion does not authorise the next T-series. Independent T-series may overlap only when dependencies and mutable outputs do not conflict. |
| E-series | Tianhang may authorise one isolated hypothesis test with a single clear instruction; no roadmap edit is required first. | Experiment-local code and outputs, plus coordinating-agent lifecycle rows in `CURRENT_STATE.md`, `WORK_INDEX.md`, and `EVIDENCE_INDEX.md`. No other shared-state change, formal baseline/protocol change, sealed-test access, or automatic promotion. |
| R-series review | Read-only inspection of existing code, protocols, literature, data descriptions, or results. | The reviewed subject and project implementation remain read-only. A requested persistent report may be written under `docs/reviews/`, with coordinating-agent lifecycle/index updates where needed. No training/scoring, protocol change, sealed-test access, or new experimental result. |

Use `R-series review` where it could be confused with Protocol R.

## E-series Isolation and Promotion

Before its first evidence-producing execution, an E-series must:

- have the coordinating agent allocate and reserve its ID, direct name, owner,
  exact mutable root, `registered` status, and pending design anchors in the
  single machine-readable `## Active E-series Registry` table in
  `docs/CURRENT_STATE.md`, then add the durable identity to
  `docs/WORK_INDEX.md`; this registration is included in the
  single-instruction E-series authority, and delegated workers must not
  self-assign IDs or edit the registry;
- create `experiments/E###-direct-name/`;
- record its hypothesis, baseline, one main variable, invariants, data scope,
  primary metric, acceptance rule, seeds/folds, and claim scope in
  `design_manifest.json`, including whether it is a `comparison`,
  `diagnostic`, or `feasibility` experiment;
- freeze that design, write its SHA-256 to `design_manifest.sha256`, and make a
  design-only commit containing only the registered experiment's design,
  source, configuration, and environment inputs, with no `EXPERIMENT.md`,
  `commands.log`, result, table, figure, or other evidence-producing output.
  Referenced data/artefact manifests must already be tracked and committed before
  this anchor;
- have the coordinating agent update the active registry row to
  `design_frozen` with the exact 64-hex design SHA-256 and 40-hex design commit
  before any evidence-producing execution. The checker must be able to read the
  design from that commit, reproduce the hash, verify its allowed path scope,
  and detect active or archive-local frozen-input drift.

After that anchor is recorded, `design_manifest.json`,
`design_manifest.sha256`, and every committed design input are immutable and
must remain byte-identical to the anchor while the E-series is active.
Archive-local frozen snapshots remain immutable after closure; shared inputs
outside the experiment root are verified at the recorded commit and may evolve
later without invalidating the archived experiment. `EXPERIMENT.md` and
`commands.log` are
mutable lifecycle records: initialise them only after registry-anchor validation;
they are excluded from the design-only commit and may be appended during
execution. If the design
changes, supersede it explicitly; do not rewrite the frozen commit or acceptance
rule. The canonical result belongs in root-level `result.json`, which
persistently references both the frozen design hash and design commit after the
active registry row is closed; aggregate tables belong in `tables/`.

The experiment owns its complete registered directory. Its record, design,
scripts, configurations, work, cache, models, outputs, and results must not be
shared as mutable paths with another track. Machine-readable files must validate
against the schemas in `schemas/`.

Every small repository-resident provenance input named by a frozen design must
be Git-tracked, use canonical LF text bytes where applicable, and match its
recorded content hash. Reject CRLF or other carriage returns before hashing; a
worktree-only file is not reproducible provenance. Large, ignored, external, or
model artefacts are referenced through a tracked artefact manifest containing
their content hash, stable locator, origin, fit-data roles, and availability
limits. Repository-wide checks validate that manifest, not the continued local
presence of the large artefact.

Multiple E-series may run in parallel. Each owns its mutable work, cache, run,
model, and output directories. They may share only immutable inputs identified by
manifest or hash. Shared baseline code and data remain read-only; an experimental
change uses an experiment-local copy or patch with provenance and hashes.

The coordinating agent updates the shared lifecycle indexes serially. The
`Active E-series Registry` is the only live E authority source; prose,
experiment folders, branches, and partial string matches do not grant authority.
A delegated experiment worker must not edit shared indexes or allocate its own
ID. On closure, the coordinator first persists the design hash and commit in
`result.json`, makes the durable indexes link to that canonical result, and only
then removes the row from the active registry. The indexes do not duplicate the
hash values; removing the live row must not remove the durable result anchor. A
design superseded before execution still uses `result.json`, with
`lifecycle_status: superseded_before_execution`, `outcome: not_applicable`, and
the replacement E-series ID; it is not an invalid experimental result.

Executed E-series outcomes are `supported`, `not_supported`, `inconclusive`, and
`invalid`; `not_applicable` is reserved for a design superseded before any
evidence-producing execution.
Negative and inconclusive experiments may be archived and do not block other
work. Coding errors, inactive configuration, contaminated outputs, leakage,
interrupted runs, and arbitrary parameter attempts are invalid execution, not
research conclusions. Near-duplicate hyperparameter settings belong in one tidy
table and one experiment record.

Promotion is:

`E-series candidate -> Tianhang approval -> named T-series -> formal revalidation -> decision update`

An E-series result may use `propose_promotion`; it must never use a direct
`promote` action. Archive quality alone never promotes exploratory evidence. Detailed recording and
dissertation-evidence rules are in
[`docs/RESEARCH_EVIDENCE_STANDARD.md`](docs/RESEARCH_EVIDENCE_STANDARD.md).

## Protocol and Evidence Safety

- Protocol names and evaluation contracts take their current meaning only from
  the latest accepted decision records; live conflicts and candidate/locked-test
  identities belong in `docs/CURRENT_STATE.md`.
- Partition the earliest admitted ordered signal before event-dependent
  transformations, reset state at every declared boundary, and fit learned
  preprocessing on training roles only. Claim `raw-time blocked` only when
  original timestamp provenance is verified; otherwise use the exact ordering
  contract supported by the admitted data.
- Do not lock or score a formal test while the evaluation population, output
  semantics, metric definitions, uncertainty reporting, or exact test manifest
  required for that claim remains unresolved.
- Current candidate-test identities and lifecycle belong in
  `docs/CURRENT_STATE.md` and accepted decision records. Candidate or locked test
  data, labels, predictions, metrics, feature feedback, and learned or selected
  artefacts derived from them must not guide ordinary development. Record any
  prior compatibility-only access and do not reuse its learned state as a clean
  Protocol R baseline.
- Keep aggregate-main-only, label-assisted, oracle, compatibility, formal
  research, deployment, and historical evidence distinct.
- Track and evidence grade are independent: T-series is not automatically a
  Protocol R result, and E-series is never formal without promotion.
- Keep REDD, matched-event CSVs, models, caches, environments, and large generated
  outputs out of version control. Do not overwrite archived results; append and
  link corrections.
- A development experiment may use only a schema-valid development-data
  manifest whose admitted roles are non-test roles and whose sealed-test flag is
  false. A caller-supplied JSON file or a self-declared safety Boolean is not an
  access control.
- Formal development code must load data through an approved manifest and
  declared role. It must not discover houses or splits with an unrestricted
  filesystem glob. A task that introduces the formal loader must include an
  automated refusal test for candidate-test and locked-test access in development
  mode.
- A collection of binary appliance models does not by itself define simultaneous
  positives, all-negative/reject behaviour, conflict resolution, accuracy or
  confusion-matrix aggregation, model-size accounting, or per-model versus
  end-to-end latency. The accepted evaluation contract must define every
  applicable item before formal scoring.

## Git and External Actions

- Do not delete or overwrite user files without explicit authorisation.
- An authorised T/E-series may use existing dependencies and may create an
  experiment-local environment from an already reviewed lock file. Installing a
  new or unpinned package, modifying a shared environment, or enabling shell
  network access requires explicit authority.
- An authorised T/E/R or direct-governance instruction includes the task-scoped
  Git commits and GitHub checkpoint needed to preserve newly created task files and
  permitted lifecycle/index updates. Unless Tianhang requests local-only work,
  push those records to a non-default branch and open or update a draft pull
  request at a safe checkpoint. Never sweep in unrelated work.
- Tianhang's standing append-only completion-sync authority permits a completed
  new task to archive, commit, and fast-forward push directly to the GitHub
  default branch without a second prompt only when the task adds new scoped
  implementation/records/evidence plus required lifecycle/index updates and
  does not modify pre-existing implementation, an accepted protocol, a
  historical record, or an accepted conclusion. All declared checks must pass,
  the worktree must contain no unrelated changes, and the live remote default
  branch must still be the expected fast-forward base. Never force-push. A
  task-specific local-only/no-push instruction or any change to existing code,
  protocol, history, or conclusions overrides this standing authority and
  requires a current explicit sync decision.
- This implicit checkpoint authority does not permit merging into the default
  branch, changing remotes, publishing outside this repository, accessing a new
  external source, operating hardware, or expanding the authorised research
  scope. Those actions still require explicit authority.
- A clear instruction authorising a new E-series includes its exact registration,
  design-only anchor, append-only run/debug records, result archive, required
  lifecycle/index updates, and the task-scoped commits/checkpoint above. It does
  not authorise another experiment, formal promotion, sealed-test access, or an
  unrequested modification to shared implementation or protocol files.
- Existing experiment records are append-only after execution begins. Correct
  historical evidence through an erratum, supersession note, or a new linked
  record; do not silently rewrite it.
- Before an authorised archive or publication, inspect status, provenance,
  credentials, absolute paths, and unexpectedly large files.
- Copy rather than move evidence until the archive and checksums are verified.
- Report final Git state after an authorised Git task.
- The GitHub default branch is the canonical published project state. Important
  evidence must not remain only on an unmerged branch. A branch or pull request
  may preserve review history, but durable work identity and evidence location
  belong in `docs/WORK_INDEX.md` and `docs/EVIDENCE_INDEX.md`.
- A pull request containing an E-series design anchor must preserve its commits
  with a merge commit. Squash or rebase merging is prohibited because it destroys
  the durable `design_commit` identity. CI and local validation require full Git
  history, not a shallow checkout.
- `README.md` must point to live status rather than duplicate fast-changing
  authorisation text. Before handoff, reconcile the worktree, default branch,
  `CURRENT_STATE.md`, and open evidence branches or pull requests.

## Language and Human Review

- English is the authoritative control language for `AGENTS.md`, AI prompts,
  schema keys and enum values, configuration, identifiers, commands, file names,
  branch names, and code symbols.
- Human-facing entry points, current-state records, plans, experiment reports,
  decision explanations, reviews, and dissertation notes use Chinese narrative
  with precise English technical terms where useful.
- T/E/R reports begin with a short English structured `Agent Brief`; the
  question, method, interpretation, limitations, and next decision are written
  primarily in Chinese.
- JSON and CSV field names remain English. Paper-ready figures and table columns
  should normally use English when they are intended for the dissertation.
- Code comments are concise Chinese by default; preserve standard English domain
  terms and do not translate identifiers.
- Maintain one authoritative mixed-language document. Do not create separate full
  Chinese and English copies that can drift apart.
- Historical immutable records do not require bulk translation. When an active
  record is materially revised, apply this policy without rewriting its verified
  facts.

## Implementation and Completion

- Use direct domain names, explicit control flow, and short stage comments.
- Comment non-obvious assumptions, units, boundaries, and algorithm choices; do
  not narrate self-evident code.
- Avoid speculative abstractions, unused wrappers, broad `try/except` blocks,
  promotional prose, and unrelated rewrites.
- Preserve parameters, measurements, limitations, and uncertainty. Do not rewrite
  a mixed or negative result as a positive claim.
- Do not end a work session or start a materially different attempt while a
  meaningful observation exists only in chat, terminal output, or an untracked
  workspace. Record the smallest recoverable checkpoint first. Valid positive,
  negative, and inconclusive results receive their declared archive; bugs,
  interrupted runs, and invalid configurations receive a concise debugging or
  invalid-run record so they are not later mistaken for missing work or evidence.
- Near-duplicate parameter runs may be compressed into one tidy table and one
  interpretation; record the search family and decision rather than producing
  repetitive prose.
- `PROJECT_PLAN.md` defines direction, not live permission.
  `docs/WORK_INDEX.md` is the durable ID-and-name index.
- `docs/EVIDENCE_INDEX.md` maps research questions and claims to exact evidence.
  `docs/reviews/R001-legacy-evidence-and-reuse-map.md` is the navigation layer
  for external and historical repositories; it does not promote their results.
- A draft, template, roadmap row, or `Pending` entry is not approval.
- Do not mark work complete without its declared checks. A completed E-series may
  close without waiting for unrelated work; do not automatically begin another
  T-series or promote an E-series.
