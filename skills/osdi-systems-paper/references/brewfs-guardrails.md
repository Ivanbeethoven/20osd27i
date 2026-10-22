# BrewFS-specific checks

Based on research scope supplied 2026-10-22; revalidate against the selected commit.

## Preserve the working title's terms

**BrewFS: Delta-Based Multi-Agent Workspaces with Packed Metadata and Variable-Granularity Object Storage**

- **Delta-Based:** private upper changes over a shared immutable baseline. Do not imply byte-delta compression, per-field logs, or invention of overlay semantics.
- **Packed Metadata:** selected read-only directory subtrees become immutable filesystem snapshots on object storage. Explain name ranges, directory entries, hot attributes, data locators, and paged indexes. Do not reduce the representation to a “metadata packet.”
- **Variable-Granularity Object Storage:** final uploaded object size differs from original file size. EC coding block `B` differs from physical read/checksum unit `q`. Describe the backend's accepted, persisted layout and read interpretation.

## Bound implementation claims

Trace lower lookup, getattr, readdir, and read separately. Scope database independence to the relevant lower path; mutable uppers and control records may use metadata storage.

Do not infer reduced redundancy ratio from a smaller coding block. For fixed data/parity counts, measure padding, checksum, and rewrite effects separately. Define write-amplification accounting before claiming a reduction.

Check whether a layout hint also changes client reads. Whole-object fetching can confound backend range granularity: factor these decisions separately.

Retain actual model and harness versions in workload records. Keep AX deployment scaffolding distinct from demonstrated end-to-end integration.

Keep ordinary volumes, legacy workspaces, entity workspaces, packed mounts, and Native Base paths separate. A feature in one path is not automatically available in another.

## Model and correctness

Define `W_i = Resolve(S, Δ_i)` as a logical model, then show how actual paths realize it. Cover visibility, deletion markers, rename, hard links, truncation, holes, publication ordering, stale readers, crashes, and reclamation according to supported semantics.

Separate namespace-view isolation, file-data isolation, and access-control enforcement. Functional tests do not prove all concurrency histories.

## Novelty obligations

Compare overlay/COW workspaces, immutable/lazy images, metadata aggregation/indexing, and erasure-coded object stores. Explain the additional difficulty of composition. If one mechanism's independent or end-to-end benefit is weak, report that and revise the claim rather than forcing three equal contributions.
