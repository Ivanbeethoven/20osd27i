# Experiment protocol assets

All files in this directory are **plans or empty collection templates**. No experiment has been executed by these files, and no performance result is supplied.

- `matrix.csv`: E00--E16, mapped to RQ1--RQ7. E00 is an integration/measurement gate; E01--E16 are planned studies.
- `run-manifest.example.yaml`: planning-only manifest. Nulls denote missing real observations. `target_resources` is a proposal, separate from `observed_environment`.
- `observations.schema.json`: a schema for future per-run aggregate observations, including actual object layout and completion status.
- `metrics-template.csv`: header only; no invented rows.
- `implementation-backlog.csv`: code and instrumentation prerequisites. A flag named in a plan is not necessarily an existing CLI parameter.

The complete method is in `../planning/02-experiment-plan.zh.md`. The paper condenses this method into its Evaluation Plan. Neither the schema nor the validation helper is a benchmark runner.

## Execution order

1. Freeze a runtime path, source revisions, real configuration and durability contract.
2. Complete and verify E00, including strict durable PUT, effective (B,q), mounted object sizes and actual mount identity.
3. Capture a variance/compatibility pilot without selecting tasks by treatment speedup.
4. Freeze task lists, repetitions, endpoints and exclusions before the confirmatory runs.
5. Run controlled mechanisms before multiplying the live-agent matrix.
6. Preserve failures, no-treatment cases, negative results, raw records and environment changes.

Do not convert `status: planned` to `executed` merely by filling in a machine name. Executed records require actual raw files, hashes, configuration, outputs and observed layout. Do not infer a new layout from an enable flag.
