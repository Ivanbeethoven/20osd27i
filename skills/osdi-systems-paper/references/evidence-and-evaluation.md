# Evidence and evaluation design

## Claim ledger

Use `claim_id`, `claim_text`, `kind`, `source_id`, `locator`, `commit_or_version`, `evidence_state`, `required_experiment`, and `limitation`. Separate design claims, code observations, derivations, measurements, and hypotheses. Code can show a path exists; it cannot show how often agents use it or how much faster it is.

Keep bibliographic provenance: exact title, authors, venue, year, URL, verified DOI if any, access date, and supported proposition. Prefer the published title when preprints differ. Record unavailable sources. Parsing BibTeX does not verify a reference.

## Experimental record

| Field | Required content |
|---|---|
| Hypothesis | Conditional, falsifiable statement |
| Intervention | Mechanism or configuration changed |
| Baselines | Strong alternatives and matched internal controls |
| Controls | Semantics, durability, resources, cache, placement, concurrency |
| Workload | Provenance, version, distributions, task selection, exclusions |
| Metrics | Numerator, denominator, collection layer, aggregation |
| Independent unit | Task, run, host allocation, or deployment—not correlated I/Os |
| Analysis | Effect size, uncertainty, timeout/failure handling |
| Falsifier | Outcome weakening or limiting the claim |
| Reproducibility | Commands, configs, seeds, commits, raw logs, plotting inputs |

Plan repetitions from pilot variance and intended precision. Preserve task pairing. Do not treat correlated I/Os as experiment repetitions. For live agents, use task-level resampling or a hierarchical analysis for nested runs. A nonsignificant test does not establish no regression.

## Fair comparisons

Separate semantic and performance matrices. Name remote sharing, clone isolation, crash consistency, durability, cache persistence, and concurrent-access guarantees. Keep semantic differences visible when exact equivalence is impossible.

Use complementary evidence: end-to-end execution for practical benefit; controlled replay for reproducibility; microbenchmarks for critical paths; ablations for necessity; fault injection for reachable failures; sensitivity and adverse workloads for boundaries.

Count costs required to obtain the benefit: snapshot construction/upload, indexing, initial materialization, rebuilds, garbage collection, peak memory, cache, storage, CPU, network bytes, request count, and recovery. Define per-workspace, per-baseline, and amortized accounting with explicit populations and lifetimes.

## Agent controls

Pin harness and actual model identifier; hold repository, task, prompt, token/turn budget, tools, timeout, concurrency, and retries fixed. Preserve success alongside time and cost: faster failure is not an improvement. Separate storage-critical time, model service time, and elapsed time. A request distribution is an observation, not causal evidence. Do not generalize one trace to all agents or tasks.

## Outcome discipline

Use planning language for unexecuted studies. Do not fabricate means, intervals, error bars, sample sizes, or measured-looking synthetic plots. Label result-table scaffolds as planned fields. Do not promise novelty or acceptance from a checklist; plan experiments that can disprove the story.
