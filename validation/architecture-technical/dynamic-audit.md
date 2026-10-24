# Per-object layout visual audit

Audited 2026-10-23 against `paper/sections/06-layout.tex`, `evidence/source_evidence.md`, and `../brewfs-upstream/src/cadapter/s3.rs` (the local client implementation).

## Recommended diagram

Use **Per-object EC layout** as the panel title. The implementation selects and persists a layout at the finalized-object boundary; it does not optimize or change it for each read request.

Show two small layout examples with **EC 2+2** written once:

| Example | EC block B | Logical shard s = B/2 | Verification quantum q | Depiction |
|---|---:|---:|---:|---|
| A | 256 KiB | 128 KiB | 64 KiB | Two q cells within each shard |
| B | 1 MiB | 512 KiB | 512 KiB | One q cell per shard |

These examples give the reader a visible distinction between the coding block B and the smaller physical unit q. If object partitioning is also shown, use the same illustrative 1 MiB finalized object under two fixed policies: four B blocks versus one B block. This is a capability illustration, **not** the current automatic policy, performance data, or a byte-scaled drawing of the shard insets. Label as **layout examples** in the caption. A 256 KiB / 4 MiB pair is also valid (q = 64 KiB / 1 MiB), but both have two q cells per shard, so it communicates q less clearly.

Use only these three flow labels where possible:

1. **Finalized object** (client knows L after compression/framing)
2. **Layout hint** (client requests a B)
3. **Admit & persist (B,q)** (RustFS validates B and selects eligible q)

For a tighter panel, reduce to **Hint → Persisted (B,q)**. Put eligibility and the static policy in the figure caption, not inside the illustration.

## Evidence boundaries

- Fixed B choices are 64 KiB, 256 KiB, 1 MiB, and 4 MiB.
- Current auto emits no hint for L <= 1 MiB and requests B = 1 MiB for L > 1 MiB; the audited server default is also B = 1 MiB. Do not depict the examples as auto choosing small B for small objects and large B for large objects.
- q is a backend choice subject to q dividing s and q*d dividing B. Both new-write gates must be enabled, and the object must be eligible. They are off by default. q is not an arbitrary user knob.
- For B = 1 MiB under 2+2, q equals s = 512 KiB; no new framing marker is needed. Reads and healing use the object's persisted layout, including applicable defaults/markers, rather than current client policy.
- B is not object length, file length, BrewFS chunk size, S3 multipart part size, a packed compression/authentication frame, or a FUSE request size.
- The strict durable create-only Entity path, Entity configuration, and packed fixture configuration retain audited hint wiring gaps. A full-path diagram must be identified as the design/interface, rather than implying all connections are already enabled.
- The Entity upper currently uploads at most 1 MiB per object, and whole-object SHA-256 verification precedes extracting upper read ranges. Do not draw a 4 KiB application read turning directly into a 4 KiB q read on that path.
- Changing B or q does not change the nominal EC redundancy ratio for a fixed d+p, and no measured reduction in amplification should be attached to these examples.

## Suggested caption sentence

“The storage inset illustrates two supported per-object layouts for EC 2+2; smaller verification frames require eligible new objects and enabled backend gates. Layouts are schematic and do not depict the current automatic hint policy.”
