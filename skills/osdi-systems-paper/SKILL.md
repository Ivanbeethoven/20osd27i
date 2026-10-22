---
name: osdi-systems-paper
description: Develop and revise evidence-grounded systems-paper arguments, English prose, LaTeX manuscripts, and experiment plans for OSDI and related systems venues. Use for research based on a code repository or design specification, especially when implementation status and unmeasured hypotheses must be distinguished. Do not treat a planning draft as a submission-ready paper.
---

# OSDI Systems Paper

## Establish the research contract

Preserve the author's chosen problem, title, terminology, and scope. State one falsifiable systems thesis before arranging sections. Explain what new constraint makes existing methods inadequate and which design decision addresses it. Separate the novelty of a mechanism from the novelty of its combination or target environment.

Use the repository as evidence, not as the paper's table of contents. Pin commits; read design specifications, actual entry points, implementation, and relevant tests. Distinguish five evidence states:

| State | Permitted use |
|---|---|
| Proposed in specification | Describe the intended contract; name the missing implementation |
| Present in code | Describe the inspected mechanism with path and commit |
| Integrated into a runtime path | Name the actual entry point and configuration |
| Experimentally observed | Report traceable measurements with workload and conditions |
| Unresolved | Keep in the issue ledger or state the uncertainty explicitly |

Do not upgrade code presence to tested correctness, a harness to a completed experiment, or an expected benefit to a result. Keep these distinctions concise in the manuscript and detailed in the research ledger.

Read [venue-and-style.md](references/venue-and-style.md) for the verified OSDI 2027 rule snapshot and structural guidance. Recheck the official CFP for the actual cycle before asserting compliance.

## Build the argument and evidence map

Map each principal claim as:

`problem → observed or proposed workload property → mechanism → invariant/trade-off → experiment → evidence status`

Explain the strongest simple alternative before presenting the mechanism. Do not define novelty by excluding a close baseline or by attaching an AI-agent label to a known storage technique.

Build a source registry before writing citations. Open primary sources and verify title, authors, year, venue, URL, and the passage supporting each claim. Use the official publication version when available. Treat search snippets, surveys, and citation databases as discovery aids. Label preprints and software documentation. Leave unsupported claims unresolved; do not invent plausible BibTeX entries or DOIs.

Read [evidence-and-evaluation.md](references/evidence-and-evaluation.md) when planning measurements, selecting baselines, or auditing causal claims.

## Write the manuscript

Organize the narrative around the scientific argument, using an adaptable progression:

1. **Introduction:** concrete problem, existing approach and its limit, central insight, mechanisms, and bounded contributions.
2. **Background and motivation:** concepts and evidence needed to derive the design. Label unmeasured workload expectations as hypotheses.
3. **Model and guarantees:** sharing, ownership, consistency, failure assumptions, and exclusions before algorithms.
4. **Design:** a critical operation through the system; for each mechanism specify representation, lookup/update path, invariant, and cost.
5. **Implementation:** prototype and integration boundaries that affect the argument. Put file inventories outside the paper.
6. **Evaluation or evaluation plan:** named questions, matched configurations, component effects, costs, and failure cases.
7. **Related work:** relevant comparison criteria, acknowledged overlap, and distinctions still needing evidence.
8. **Limitations and conclusion:** supported scope and remaining uncertainty, without new claims.

Keep an abstract self-contained. In a planning draft, describe design and evaluation intent without invented speedups or wording that implies completed experiments. In a completed paper, derive the abstract from the measured evidence.

Prefer concrete English subjects and verbs. Define terms and symbols at first use. Put known context early and the new consequence later. Use one paragraph for one causal step. Preserve technical precision when shortening prose. Remove promotional qualifiers, repeated contribution lists, unexplained labels, and unsupported superlatives.

Read [english-revision.md](references/english-revision.md) for revision checks and [sources-and-attribution.md](references/sources-and-attribution.md) for sources consulted. These guide structure, not text to reproduce.

## Design experiments before results

For each research question, record hypothesis, intervention, baseline, controls, workload, independent unit, metrics, repetitions, uncertainty treatment, planned figure, and an outcome that weakens the claim. Separate proposed hardware from hardware actually used.

Measure end-to-end benefit and mechanism behavior. Hold semantics, durability, cache budget, resource placement, and backend policy constant wherever causality requires it. Where parity is impossible, report the difference and avoid one undifferentiated ranking.

Plan negative controls and boundary workloads. Separate representation, caching, compression, batching, replication, and layout effects. Include setup and maintenance costs needed to obtain the headline benefit. Do not silently omit failed or unsupported workloads.

For AI agents, separate reproducible replay from live-agent validation. Pin the model identifier, harness, prompt/task, tool policy, token limits, task set, and timeout handling. Do not attribute inference variance to storage or equate trace distributions with performance results.

For BrewFS, also read [brewfs-guardrails.md](references/brewfs-guardrails.md). Revalidate those checks against the pinned code; they are not timeless implementation assertions.

## Produce and verify artifacts

Use the official template, preserve notices, and record URLs and hashes. Do not change margins, fonts, line spacing, or figure text to fit a limit. Put extensive plans and evidence tables in accompanying research documents; the submission must remain self-contained.

Compile LaTeX with bibliography processing, check unresolved citations/references, inspect every rendered page, verify legibility and font embedding, and confirm content-page count. Keep source, figures, bibliography, build instructions, and verification notes together. Compilation does not verify research claims.

Keep a visible draft status and unfinished evidence list for internal drafts. Respect actual anonymity and AI-use policies. OSDI 2027 permits AI editing but prohibits submission of wholly or largely AI-generated work; a substantial generated working draft requires author-led scientific writing and validation before submission. Do not submit or declare compliance on the author's behalf.

Save deliverables through the applicable persistence workflow. Install skills only through an authorized storage route. Do not bypass a denied protected-directory write; report installation failure separately from delivery of a portable skill package.
