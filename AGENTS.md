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
- Conversation summaries and reported results are context, not local execution
  evidence. The inspected worktree and locally verified outputs are authoritative.
- Preserve historical records as historical records; correct them through a
  current-state update or supersession note.

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
- Do not commit, push, modify remotes, open pull requests, publish, access a new
  external source, or operate hardware unless the current instruction includes
  that action, except for the narrowly scoped local E-series lifecycle commits
  below.
- A clear instruction authorising a new E-series automatically includes the local
  commits strictly required to register its identity, create its design-only
  anchor, and record that anchor in the active registry. Those commits may
  contain only the exact shared registry/index rows and registered experiment
  design inputs required by this lifecycle; they must not sweep in unrelated
  work, results, or another track. This exception does not authorise executing
  beyond the E scope, archiving results, pushing, opening a pull request,
  publication, remote mutation, or any other external action.
- One instruction may additionally authorise an E-series and specified
  archive/Git actions together; unstated external actions are not implied.
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
- `PROJECT_PLAN.md` defines direction, not live permission.
  `docs/WORK_INDEX.md` is the durable ID-and-name index.
- `docs/EVIDENCE_INDEX.md` maps research questions and claims to exact evidence.
  `docs/reviews/R001-legacy-evidence-and-reuse-map.md` is the navigation layer
  for external and historical repositories; it does not promote their results.
- A draft, template, roadmap row, or `Pending` entry is not approval.
- Do not mark work complete without its declared checks. A completed E-series may
  close without waiting for unrelated work; do not automatically begin another
  T-series or promote an E-series.
