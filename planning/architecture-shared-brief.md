# Shared-base architecture draft

This is a continuation of the authorized compact BrewFS figure revision.
The user redirected the takeover on 2026-10-23 toward studying the four OSDI
method diagrams and making BrewFS's central idea visually clear.

## Visual argument

Two independently writable views refer to one pinned immutable snapshot.
Private Data spans differ between views, while explicit LowerRange spans may
refer to the shared lower. Packed records explain how the lower is accessed;
the backend inset explains a distinct per-object persisted layout contract.

The main area uses about two-thirds of the width for the shared-base relation.
The right inset is subordinate. Final canvas: 504 × 230 PDF points, exactly the
same footprint as the previous compact figure. Minimum live text: 8 pt.
Blue/pale blue consistently identifies the immutable lower; pale amber identifies
private payload, and gray identifies parity or backend policy. This semantic palette uses
two pale families rather than pretending every colored component is novel.

## Components and edges

- Workspace i/j: logical views, not physical servers. Their Δ records are current
  private state in the mutable metadata service. The metadata-service placement
  is explained in the caption rather than by an inaccurate enclosing box.
- Two illustrative file maps use the same A/B/C logical range coordinates;
  workspace i modifies B and workspace j modifies C. Lower labels denote explicit
  LowerRange and Data labels denote private replacements. Hole is explained in
  the caption but omitted from this focused overwrite example.
  Data arrows reference private payload objects outside the view boxes. The maps are not measured
  workload distributions and their lengths are not quantitative. The payloads
  reside on object storage, not in client memory. Δ records reside in the mutable
  metadata service, as explicitly labelled.
- pin S edges bind each view to the same snapshot identity. They do not prescribe
  a read execution sequence. Name resolution checks upper visibility first.
- Snapshot S contains manifest roots, the representative directory-name route,
  GroupMeta records, and packed data frames. Other queries use other indexes;
  LowerRange reads need not repeat a name lookup.
- Backend: finalized object length -> pending hint -> admission -> stored layout.
  The two-data/two-parity example uses B=256 KiB, s=128 KiB, q=64 KiB. The
  selector example requires eligible objects and both new-write gates enabled.
- The snapshot/backend edge denotes object access under a stored layout, not
  one-to-one correspondence of Packed frames and q cells, or a fixed GET count.

## Scientific boundaries

Sources: sections/03-overview.tex through 06-layout.tex and
evidence/source_evidence.md. This revision changes presentation only.

1. Explicit-map gaps do not implicitly inherit lower data. Hole reads zero.
2. Upper GET verifies the complete object before slicing; short FUSE reads are
   not necessarily short storage reads. PUT-before-map-publication stays in text.
3. h uses finalized object length, not FUSE size. Entity strict PUT and producer
   hint paths are integration obligations. No automatic optimization is claimed.
4. q differs from a Packed authentication/compression frame and is constrained by
   the coding geometry. Reads/repair use stored layout, not today's write gates.
5. Snapshot sharing is a representation, not measured cross-task overlap or an
   established performance benefit. The diagram is an author-review draft.

## Borrowed visual methods, not copied artwork

- Oxbow Fig.3: let spatial ownership carry meaning. Fig.4-8: show records and
  operations when a mechanism cannot be understood from component names alone.
- Dingo Fig.12-13: overview followed by a concrete operation/representation.
- Umap Fig.1/5: comparable views and a visible address/segment representation.
- CoPilotIO Fig.4: large responsibility regions and a small executable example.

All sources are the user's local OSDI 2026 PDFs. Extracted originals and
per-paper notes are in ../../outputs/osdi26-writing-study/. This artwork is
drawn from scratch, with editable SVG text; it reuses no original artwork.
