# Real-Time rTM NILM System

This directory is the public-facing implementation workspace for the MSc
prototype. Its contents are intended to become the code presented or released
as the runnable system.

The implementation has not yet been assembled here. Files will be added as the
minimum end-to-end workflow is built, using clear functional responsibilities
such as data supply, feature and Boolean input construction, model definition,
training, evaluation and chronological replay. The final structure will follow
actual code needs rather than a pre-generated framework.

The selected model family is TMU 0.8.3 `TMRegressor` with integer-weighted
clauses. Exact features, Booleanisation, target transformation and training
configuration are intentionally not implied by that model choice.

This workspace may contain:

- runnable source code and thin command-line entry points;
- required public configuration;
- focused tests for the runnable path and material failure modes;
- concise installation, usage and example documentation.

It does not contain:

- raw or redistributed REDD data;
- agent instructions or repository governance;
- internal task, review or experiment records;
- private reference files, temporary runs, caches or trained artefacts.

During development `system/` remains part of the surrounding research
repository; it is not a nested Git repository. Public code should remain usable
without runtime imports from the surrounding internal documentation and
governance files.

## Development style

This is a supervisor-reviewed MSc prototype. It is developed in small,
reviewable increments so that its control flow, definitions and outputs can be
explained directly in VS Code and demonstrated from a simple command.

Code favours concrete names, clear functional modules and visible data flow.
Comments briefly explain definitions, units, causality or boundary rules,
assumptions and design intent where they are not obvious. They do not repeat
routine syntax or provide defensive explanations for hypothetical behaviour.
