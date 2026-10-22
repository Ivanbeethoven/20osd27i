# Review resolution — 2026-10-22

This file records how the preparation package resolved substantive review findings. The individual review files preserve their original observations; they are not a list of remaining defects. No review or package check executed BrewFS or established benchmark outcomes.

| Review topic | Resolution in the delivered draft and protocol |
|---|---|
| Title and scope | Retained the requested title. Framed the contribution around shared baselines, private state, lower metadata access and object I/O. Removed first-of-kind implications for overlay/COW or object-stored immutable metadata. |
| Distinct runtime paths | Separated ordinary/legacy VFS, experimental fresh Entity, standalone Packed and Native Base; the mechanism ablations require same-path adapters. |
| Three missing hint connections | Added Entity S3 configuration, Packed producer and strict durable create-only PUT gates; conditional upload semantics must remain intact. |
| Upper object formation | Recorded Entity FUSE MAX_WRITE=1 MiB and direct upload formation. Mounted upper auto does not exercise its >1 MiB branch; fixed hints and other finalized-object paths are separate experiments. |
| Physical layout and q | Recorded default-off new-write gates, eligibility, persisted layout, new-object-set requirement and geometry-dependent no-op cases. Four remote servers do not activate the all-local batch-pread path. |
| Client confounding | Separated Range/full-object fetch, SingleFlight/cache, retained write-budget release and shared-buffer replies. Full-object upper integrity remains in the measured path. |
| Resource accounting | Limited the delta accounting identity to disjoint live logical metadata categories. Physical payload, EC/checksum, unreclaimed objects and caches are separate. Additive build costs use the same units; concurrent makespan is not the sum of task wall times. |
| Parameter notation | Replaced ambiguous B/q notation with the parameter pair (B,q) in the paper, current planning text and machine-readable experiment tables. Identical ratios are not treated as identical layouts. |
| Mandatory strong baseline | Added at least one feasible CernVM-FS/Nydus immutable lower plus writable upper to the core comparisons, with construction and any required checkpoint cost. |
| Durability fairness | Separated local workspace service from remote durable service. BranchFS ephemeral fsync is not used as an equivalent remote-completion point. |
| Legal factorial comparisons | Marked missing D/P/C adapters as implementation work, allowed nested designs, and prohibited fabricated combinations or a path switch presented as one-factor ablation. |
| Cache/directory/lifecycle limits | Preserved the Packed CLI payload-cache restriction, Entity directory/owner limits, fresh-only mount boundary, and implementation gates for recovery/reclamation studies. |
| Sample budget and statistics | Added an explicit 180-run core and 540-run extension; randomized paired blocks and task/repository clustering; failures and timeouts remain in primary outcomes. |
| Literature accuracy | Included DeltaFS, BranchFS workshop, final YoloFS, current metadata work and Okapi with scoped differences. Added verified official Pro/JuiceFS entries. Kept MesaFS full-text limitation visible rather than inferring its design. |
| Narrative clarity | Added a symbolic access example linking a shared directory entry, private data mapping and persisted layout, including the upper full-object-read boundary. |
| Final mathematical review | Addressed both mandatory manuscript findings: (B,q) pair notation and the scope of metadata-space terms. State labels remain where they change scientific interpretation. |
| Anonymity | Corrected an unconditional BrewFS name in the body; retained explicit warning that the neutral-name PDF is only a preview and requires a complete human anonymity review. |
| Skill delivery | Validated the portable skill; recorded the protected-directory auto-review denial. No installation, git synchronization or bypass is claimed. |

## Remaining research work, deliberately not presented as completed

- Implement and qualify the E00 integration gates and required controlled adapters on a new recorded research revision.
- Acquire the proposed environment, freeze actual versions/task lists, pilot variance and select formal sample sizes before inspecting treatment effects.
- Execute correctness, performance, fault, repair and longevity experiments; publish negative results and unsupported cases alongside positive findings.
- Retrieve the outstanding full text of MesaFS and complete the HMFS near-neighbor reading before final novelty claims.
- Rewrite and approve the manuscript under author control using measured evidence, then perform full anonymity and venue-policy review.

The package is complete as a research-planning and initial-writing deliverable. These remaining items belong to the subsequent implementation, experimental and submission phases requested only as plans in this task.
