# Agent Guidance

## Authority and Responsibilities

- Tianhang approves research decisions, scope changes, and external actions.
- Web ChatGPT supports discussion, explanation, research analysis, prototypes, reviews, and task specifications.
- Desktop Codex performs authorised local inspection, file editing, commands, tests, experiments, builds, Git work, and hardware work.
- Conversation claims, summaries, and web drafts are not evidence of local execution.
- The actual worktree and locally generated and verified outputs are the authoritative project state.
- `docs/CURRENT_STATE.md` may record only facts verified in the local project.

## Execution Rules

- Inspect the actual worktree and relevant governance files before making changes.
- Work only within the scope of the current named task.
- Write only content explicitly provided or confirmed by Tianhang.
- Do not expand the research plan from general knowledge, memory, or task summaries.
- Mark unconfirmed REDD houses, appliance classes, split ratios, time boundaries, purge, model architecture, and parameters as `Pending`.
- Stop and request a decision before performing work that depends on a `Pending` item.
- Do not import prototype or legacy code wholesale without a separate review and migration task.
- Prefer the smallest change required by the current task.
- Preserve existing user work and avoid unrelated rewrites.
- Report the files changed, commands run, checks performed, failures encountered, and relevant checks not run.

## Current Phase Lock

T001 completed on 2026-07-21 after Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record.

There is currently no active execution task. The project is paused pending Tianhang's next explicit authorisation and phase transition.

The following remain unauthorised:

- T002, T003, or any other later task;
- remotes, push, pull requests, or other GitHub operations;
- REDD or external repository access;
- algorithm creation or migration;
- training or experiments;
- firmware, Pico, or hardware work;
- tags or additional branches.

No later project phase begins automatically after T001.

## Git and External Actions

- Do not delete or overwrite user files without explicit authorisation.
- Do not commit, push, create or modify remotes, open pull requests, or operate GitHub unless the specific action is explicitly authorised.
- Do not include credentials, REDD data, personal absolute paths, or large temporary artefacts in version control.
- Report the resulting Git state after every authorised Git task.

## Code Style

These rules apply when a later task authorises implementation work:

- Use direct, domain-specific names.
- Keep control flow explicit and easy to trace.
- Use short stage comments only where they improve navigation.
- Comment non-obvious assumptions, units, boundaries, and algorithm choices.
- Do not explain self-evident assignments, loops, or function calls.
- Keep docstrings brief and limited to public interfaces or genuinely complex behaviour.
- Avoid tutorial-style, defensive, or promotional prose.
- Avoid long section banners.
- Do not add speculative abstractions, generic wrappers, fallback layers, or unused configuration.
- Do not use broad `try/except` blocks to hide data or schema failures.
- Match the surrounding style and avoid unrelated rewrites.
- Production code comments should normally use concise English.

## Governance Review

- All governance files are subject to item-by-item user review.
- Do not treat a draft, skeleton, or `Pending` entry as an approved decision.
- Do not mark a task complete unless its required local checks were actually performed.
- Do not continue automatically into the next task after completing the current one.
