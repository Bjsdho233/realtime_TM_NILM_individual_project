# TM NILM ISTM Lab

This repository is the clean working base for Tianhang Tan's MSc individual project on Tsetlin-Machine-based non-intrusive load monitoring (NILM).

The project aims to establish a traceable workflow from local TM training and model export to verified inference on a Raspberry Pi Pico target. Its research performance will be evaluated on REDD under a leakage-controlled protocol.

Earlier experiments and external implementations remain useful references, but they are not automatically treated as evidence produced by this project.

## Current Status

T001 governance review and local repository bootstrap are complete. The revised T002 upstream snapshot acquisition and REDD inventory is active under a limited authorisation.

**Active execution task:** [T002 — REDD Inventory and Protocol R Preflight](docs/tasks/T002-redd-inventory-and-protocol-r-preflight.md)

[T001 — Governance Review and Repository Bootstrap](docs/tasks/T001-governance-review-and-repository-bootstrap.md) is complete. T002 is limited to the authorised recursive Han snapshot acquisition, read-only REDD inventory, source-chain review, and governance evidence.

No algorithm implementation, REDD dataset, trained model, formal experiment result, firmware result, or hardware result has yet been accepted as verified evidence in this repository.

For the latest verified status, see:

- [Current State](docs/CURRENT_STATE.md)
- [Project Plan](PROJECT_PLAN.md)
- [Completed T001](docs/tasks/T001-governance-review-and-repository-bootstrap.md)
- [Active T002](docs/tasks/T002-redd-inventory-and-protocol-r-preflight.md)

## Project Goals

The project is intended to:

1. reproduce a minimum Han-compatible training-to-Pico workflow;
2. establish a leakage-controlled mixed-house evaluation on REDD;
3. develop and compare TM-based NILM improvements using training and validation evidence;
4. export the selected model and verify host-to-Pico inference parity;
5. measure embedded latency, memory use, and causal replay behaviour;
6. optionally examine held-out-house generalisation if the available data support it.

The appliance class set, data split, exact TM design, Pico configuration, real-time input boundary, and final acceptance criteria remain pending.

## Evaluation Protocols

The project separates compatibility, research, generalisation, and deployment evidence.

| Protocol | Purpose |
|---|---|
| Protocol H | Reproduce and verify the minimum Han-compatible engineering workflow. |
| Protocol R | Perform the primary mixed-house, raw-time blocked research evaluation. |
| Protocol X | Optionally test held-out-house generalisation. |
| Protocol D | Train and verify the final deployment model after the research method is frozen. |

Protocol R is the primary dissertation evaluation.

The full rules are recorded in [D002 — Primary Evaluation Protocol](docs/decisions/D002-primary-evaluation-protocol.md).

## Repository Guide

| Path | Purpose |
|---|---|
| `AGENTS.md` | Current operating rules, approval boundaries, and phase lock. |
| `PROJECT_PLAN.md` | Project direction, stages, deliverables, and success framework. |
| `docs/CURRENT_STATE.md` | Latest locally verified project state. |
| `docs/decisions/` | Accepted project decisions and their consequences. |
| `docs/tasks/` | Named task specifications, scopes, checks, and stop conditions. |
| `docs/progress/` | Append-only dated progress records. |
| `docs/data/` | Future human-readable dataset and protocol reports. |
| `scripts/` | Future approved utilities and repeatable workflow entry points. |
| `src/` | Future host-side NILM and TM implementation. |
| `tests/` | Future automated checks and parity tests. |
| `firmware/` | Future Pico inference implementation. |
| `configs/` | Future reviewed experiment and deployment configurations. |
| `artifacts/manifests/` | Future machine-readable manifests and evidence identities. |

Some implementation paths are planned but may not yet exist. They will be created only through approved tasks.

## Working Principles

- Work must remain within the currently approved named task.
- Confirmed facts, pending decisions, and historical evidence must remain clearly separated.
- Research results must be traceable to their data manifest, configuration, code revision, and generated outputs.
- REDD must remain outside the repository.
- Absolute dataset paths, credentials, secrets, and machine-specific state must not be committed.
- Code from earlier repositories may be reused only through a recorded and locally verified migration task.
- Candidate or locked test data must not guide ordinary model development.
- Compatibility results must not be presented as primary Protocol R results.
- Deployment results must not be presented as unbiased research-test results.

The complete operating rules are defined in [AGENTS.md](AGENTS.md).

## Data and Results

REDD is not distributed with this repository. The pinned Han upstream snapshot has been inventoried, but no original raw REDD copy has been verified or approved for Protocol R raw-time evaluation.

The active T002 snapshot inventory is recorded in:

- [REDD Inventory](docs/data/REDD_INVENTORY.md)
- [Protocol R Preflight Status](docs/data/PROTOCOL_R_PREFLIGHT.md)

Historical scores and observations may guide future questions, but they are not results from the new evaluation protocol unless they are reproduced and recorded under an approved task.

Formal results will be added only after their data source, protocol, configuration, and evidence files have been verified.

## Running the Project

There is currently no approved implementation or runtime environment to execute.

Installation instructions, dependencies, training commands, export commands, and Pico build instructions will be added after the relevant implementation tasks have been completed and verified.

## External References

- [Han Wu's NILM repository](https://github.com/wuhanstudio/nilm) — external technical reference implementation.
- [Previous experimental repository](https://github.com/Bjsdho233/nilm-fridge-tm-research) — read-only historical evidence.

Neither repository will be copied or merged wholesale into this project. The reuse policy is defined in [D001 — Clean Repository and Controlled Code Migration](docs/decisions/D001-clean-repository.md).

## Getting Oriented

Before beginning work:

1. read `AGENTS.md`;
2. check `docs/CURRENT_STATE.md`;
3. open the active task specification;
4. confirm that the intended action is authorised;
5. stop if the required decision, input, or approval is still pending.

Approval of a plan or task specification does not automatically authorise its execution.
