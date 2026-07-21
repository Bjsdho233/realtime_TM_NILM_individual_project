# D001 — Clean Repository and Controlled Code Migration

**Status:** Accepted\
**Date:** 2026-07-21\
**Decision owner:** Tianhang Tan

## Context

The previous project repository contains useful experimental evidence, but its development history is distributed across many branches and depends heavily on conversational context to explain its state. Continuing development directly from that repository would carry these organisational problems into the new project.

Han's repository is the current technical reference, but it should not be copied wholesale. Only components relevant to the new training-to-Pico workflow should be considered for reuse.

## Decision

The project will be developed in a new, independent repository with a clean history and explicit governance records.

The following rules apply:

- The previous project repository remains unchanged and is treated as read-only historical evidence.
- Han's repository is treated as an external reference implementation.
- Neither repository will be copied or merged wholesale into the new project.
- Historical results may guide hypotheses and planning, but they are not results produced under the new project's evaluation protocol.
- Code may be migrated only through a named review or implementation task.
- Each migration must record:
  - the source repository and revision;
  - the original file or component;
  - the reason for reuse;
  - any modifications made;
  - the local checks performed.
- Only the smallest relevant component should be migrated.
- Migrated code must conform to the new project's interfaces, evidence rules, and evaluation protocol.
- Locally verified files and outputs in the new worktree become the authoritative project state.

A clean repository does not require every component to be rewritten from scratch. It requires reuse to be deliberate, traceable, and locally verified.

## Consequences

### Positive consequences

- The current project state can be understood from the repository itself.
- Research results can be traced to specific tasks, configurations, and runs.
- Legacy assumptions are less likely to enter the new workflow unnoticed.
- Han-compatible components can still be reused where they are relevant and verified.
- Git branches can be used for code development without becoming the primary experiment record.

### Costs and limitations

- Useful legacy components require review before reuse.
- Some earlier scripts may need adaptation or reimplementation.
- Historical scores cannot be presented as new Protocol R results unless they are reproduced under the approved protocol.

## Actions Not Authorised by This Decision

This decision does not itself authorise:

- importing or modifying legacy code;
- accessing REDD;
- running training or experiments;
- initialising Git;
- creating commits, remotes, or GitHub repositories.

Those actions require separate named tasks and explicit approval.
