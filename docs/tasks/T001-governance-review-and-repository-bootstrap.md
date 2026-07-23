# T001 — Governance Review and Repository Bootstrap

> **Historical closed-task record.** References below to the 2026-07-21 phase
> lock describe the governance used when T001 ran; they do not grant current
> authority. Live authority is only in
> [`docs/CURRENT_STATE.md`](../CURRENT_STATE.md).

**Status:** Complete\
**Owner:** Tianhang Tan\
**Created:** 2026-07-21\
**Last updated:** 2026-07-21\
**Completed:** 2026-07-21\
**Task type:** Governance and repository setup\
**Dependencies:** None\
**Historical closure authority:** None; T001 is closed and there is no active execution task

## 1. Objective

Establish a coherent, locally verified governance baseline for the new project and, after separate explicit approval, initialise its local Git history.

This task must leave the project in a state where:

- the repository explains its own purpose, rules, current state, and next tasks;
- confirmed decisions are separated from pending choices;
- the actual worktree has been inspected and reconciled with the documentation;
- no algorithm, dataset, experiment, or hardware work has entered the project prematurely;
- the first Git commit contains only reviewed project-governance material;
- the next technical task cannot begin automatically.

## 2. Context

The project skeleton and several governance documents have been created manually.

The following documents have received individual review:

- `AGENTS.md`;
- `PROJECT_PLAN.md`;
- `docs/decisions/D001-clean-repository.md`;
- `docs/decisions/D002-primary-evaluation-protocol.md`;
- `docs/CURRENT_STATE.md`.

However, the complete local worktree has not yet received a consolidated inspection. The remaining governance files also require review before the project can be treated as bootstrapped.

No implementation, REDD data, trained model, generated result, firmware, or hardware evidence has been accepted into the new project.

## 3. Scope

### 3.1 In scope

- Review all initial governance and project-orientation files.
- Confirm that their terminology, task identifiers, links, and restrictions are consistent.
- Inspect the actual project tree using read-only commands.
- Identify unexpected files, generated artefacts, code, data, secrets, or existing Git state.
- Reconcile `docs/CURRENT_STATE.md` with the verified worktree.
- Confirm that unresolved technical and research choices remain marked `Pending`.
- Validate Markdown paths and the intended directory structure.
- Prepare an exact Git-bootstrap proposal.
- After separate explicit authorisation:
  - update the phase lock where required;
  - initialise the local Git repository;
  - create the first reviewed commit;
  - verify the resulting branch, commit, and worktree state.
- Record the completion of T001.

### 3.2 Out of scope

- Accessing or processing REDD.
- Selecting houses, appliances, splits, boundaries, or purge rules.
- Auditing or importing Han's implementation.
- Migrating code from either historical repository.
- Writing algorithm or firmware code.
- Installing project dependencies.
- Training or evaluating a model.
- Compiling or flashing the Pico.
- Creating a remote repository.
- Adding a Git remote.
- Pushing, opening a pull request, or publishing any project content.
- Beginning T002 or T003 automatically.

## 4. Required Files

The initial governance review covers at least:

- `AGENTS.md`;
- `PROJECT_PLAN.md`;
- `README.md`;
- `.gitignore`;
- `.codex/config.toml`;
- `docs/CURRENT_STATE.md`;
- `docs/decisions/D001-clean-repository.md`;
- `docs/decisions/D002-primary-evaluation-protocol.md`;
- `docs/tasks/T001-governance-review-and-repository-bootstrap.md`;
- `docs/tasks/T002-redd-inventory-and-protocol-r-preflight.md`;
- the initial dated record in `docs/progress/`.

Any additional file found during inspection must be classified before the first commit.

## 5. Authorisation Gates

### Gate A — Document review

Governance files may be drafted and manually saved during the current phase.

Reviewing a document does not authorise the technical work described by that document.

### Gate B — Consolidated local inspection

After the initial files have been reviewed, a consolidated read-only inspection may check:

- directory and file names;
- file contents relevant to governance;
- internal Markdown links;
- ignored-file rules;
- presence of unexpected code, data, outputs, or credentials;
- whether a Git repository already exists;
- whether the documented state matches the actual worktree.

The inspection must not modify, delete, rename, initialise, stage, or commit anything.

### Gate C — Git bootstrap

Git bootstrap requires separate explicit authorisation from Tianhang after the inspection results have been reported.

Tianhang supplied that explicit authorisation on 2026-07-21. The authorised local repository bootstrap used `main`. The initial governance baseline commit is `df8451b4eea59e1b9a3af78fa7aac72f614de8b7`.

T001 is complete after Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record. T002, T003, remotes, push, GitHub, REDD, external repositories, algorithms, training, firmware, Pico, and hardware work remain unauthorised.

Before authorisation, do not run:

- `git init`;
- `git add`;
- `git commit`;
- branch, tag, remote, push, or pull commands that change state.

The Git proposal must state in advance:

- the directory to be initialised;
- the intended initial branch;
- the files to be included;
- the files to remain excluded;
- the proposed commit message;
- any required governance-state updates.

Approval of this task document is not approval to execute those commands.

### Gate D — Phase transition

Completion of the first commit does not automatically authorise T002, T003, REDD access, code migration, or implementation.

The next task and the corresponding change to the `AGENTS.md` phase lock require explicit approval.

## 6. Procedure

### Step 1 — Complete individual document review

Review and reconcile:

1. `AGENTS.md`;
2. `PROJECT_PLAN.md`;
3. D001 and D002;
4. `docs/CURRENT_STATE.md`;
5. T001 and T002 task specifications;
6. `README.md`;
7. `.gitignore`;
8. `.codex/config.toml`;
9. the initial progress record.

Check that the same protocol names, task identifiers, project boundaries, and approval rules are used throughout.

### Step 2 — Inspect the local worktree

Perform one consolidated read-only inspection.

Record:

- the inspected root path;
- the directory tree;
- all ordinary files intended for the initial repository;
- unexpected or unclassified files;
- the presence or absence of algorithm code;
- the presence or absence of REDD data;
- the presence or absence of generated outputs;
- the presence or absence of possible secrets or machine-specific files;
- the actual Git state.

Do not expose secret values. Report only the affected file and the type of risk.

### Step 3 — Reconcile the documented state

Update the governance documents where the inspection proves that an earlier statement is incomplete or inaccurate.

In particular:

- make `docs/CURRENT_STATE.md` match the verified worktree;
- resolve broken links and inconsistent filenames;
- keep unresolved research choices marked `Pending`;
- ensure `.gitignore` excludes raw data, generated results, build artefacts, credentials, editor state, and machine-specific files as appropriate;
- keep configuration minimal and within the current phase restrictions.

### Step 4 — Request acceptance and Git authorisation

Present:

- the verified tree summary;
- any corrections made or still required;
- the proposed initial commit contents;
- the proposed initial branch and commit message;
- confirmation that no remote or push action is proposed.

Wait for explicit approval before changing Git state.

### Step 5 — Perform the authorised bootstrap

Only after approval:

1. apply the approved governance-state updates;
2. initialise Git in the exact verified project directory;
3. use the approved initial branch;
4. stage only the reviewed files;
5. inspect the staged file list;
6. create the approved initial commit;
7. verify the commit identity and worktree state.

Do not configure or publish a remote.

### Step 6 — Close T001

Record:

- whether all acceptance criteria passed;
- the initial branch;
- the initial commit identifier;
- the final worktree status;
- any known limitations or deferred corrections;
- that the next task remains unauthorised.

Update T001 and `docs/CURRENT_STATE.md` to reflect the completed state. Add a dated progress record without rewriting earlier records.

## 7. Acceptance Criteria

T001 is complete only when all applicable criteria are satisfied:

- [x] All required governance files have been reviewed.
- [x] `PROJECT_PLAN.md` has been explicitly accepted or retains an accurate review status.
- [x] D001 and D002 remain recorded as accepted decisions.
- [x] T001 and T002 have clear scope, inputs, restrictions, and exit conditions.
- [x] The complete project tree has been inspected locally.
- [x] `docs/CURRENT_STATE.md` matches the inspected worktree.
- [x] Unexpected files have been classified and resolved.
- [x] No REDD data, credentials, algorithm code, generated experiment output, or firmware artefact is included unintentionally.
- [x] Internal filenames and Markdown links are consistent.
- [x] Pending decisions have not been silently filled from historical work.
- [x] `.gitignore` covers the known categories of local and generated files.
- [x] `.codex/config.toml` does not authorise work outside the current approved phase.
- [x] Git bootstrap received separate explicit authorisation.
- [x] The initial repository was created in the verified project directory.
- [x] Only reviewed files were included in the initial commit.
- [x] The initial branch and commit were verified.
- [x] No remote, push, pull request, or publication action occurred.
- [x] The final worktree state is understood and reported.
- [x] T001 completion is recorded in the current-state and progress documents.
- [x] No later task has begun without explicit approval.

If Git bootstrap is deliberately deferred, the document-review portion may be reported as complete, but T001 remains open.

## 8. Stop Conditions

Stop and report instead of continuing if:

- the inspected path is not the intended project root;
- a Git repository already exists unexpectedly;
- the project is nested inside another Git repository in a way that changes the intended setup;
- unexpected algorithm code, REDD data, generated results, credentials, or large binary files are present;
- reviewed documents materially contradict one another;
- the proposed initial commit contains unreviewed files;
- Git identity or repository settings require an unapproved change;
- explicit Git authorisation has not been given;
- completing the task would require deleting or overwriting user work.

A stop condition must be resolved explicitly. It must not be bypassed by assumption.

## 9. Evidence

The T001 completion report must include:

- inspected project-root path;
- concise verified tree summary;
- validation findings;
- list of files included in the initial commit;
- initial branch name;
- initial commit identifier;
- final Git status;
- confirmation that no remote or push action occurred;
- remaining pending decisions;
- the next task proposed for approval.

Command output may support the report, but the repository documents remain the authoritative project record.

## 10. Exit and Handoff

After T001 is completed, the project is ready for one separately approved next task:

- **T002:** inspect the local REDD dataset and prepare the Protocol R preflight; or
- **T003:** audit a pinned revision of Han's workflow and define the minimum reproduction contract.

T002 requires the exact local REDD path. T003 requires approval to inspect the external reference repository.

Neither task begins automatically.
