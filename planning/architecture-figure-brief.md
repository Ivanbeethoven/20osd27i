# System architecture figure brief

Date: 2026-10-23. Scope: replace the small existing overview figure with a
double-column, editable system diagram. This is a logical architecture of the
paper's Entity workspace design, not a deployment topology or performance plot.
The user authorized completing the architecture figure and its editable form;
routine composition decisions below are grounded in the existing manuscript.

## Visual argument

Each workspace keeps its private current state, inherits visible unchanged
state from one pinned shared snapshot, and accesses objects whose effective
encoding/verification layout is stored by the backend. The three numbered
mechanisms match Sections 4, 5 and 6. They are contribution markers, not a
claim that every request traverses three sequential processing stages.

Start at the agent tools, then follow the workspace resolver and its two
branches. The mutable service and immutable object store occupy separate
regions. The figure must show the metadata service still exists. The lower
reader is per-client; its snapshot objects, not one shared reader process,
are reused by workspaces.

## Components and evidence

| Label / role | Container / class | Evidence |
|---|---|---|
| Agent tools: repository inspection, editing, build/test | External workload | Observed workload §2.2; not an LLM reasoning architecture |
| Workspace client i, repeated ×N | Client boundary / existing runtime with research mechanisms | §3; Entity FUSE dispatch and `src/cli/entity_mount.rs` |
| 1 Delta-based workspace, Wi = Resolve(S, Delta_i) | Client / paper mechanism | §3–4; `entity/resolver.rs`; source ledger D01–D03 |
| Private upper Delta_i: names, tombstones, span maps | Client's logical state / paper mechanism | `entity/model.rs:59–86,246–378`; Data/LowerRange/Hole; D01–D03 |
| 2 Packed lower reader | Per-client / paper mechanism | §5; `entity/packed_lower.rs`; ledger P01–P06 |
| Mutable metadata service: upper + bindings/pins/leases | Persistent mutable state / existing service | §4–5; Redis Entity mount; upper/control still requires KV |
| Private payload objects | RustFS object store / existing data storage | `entity/data.rs:400–450,826–865`; D10 |
| Shared snapshot S: manifest, indexes, pages, frames | RustFS object store / paper representation | §5; PM11/IP06/GroupMeta; P01–P04 |
| Snapshot producer: selected fixed source view, finalized objects | Construction path / existing producer | §5.3; P07–P08 |
| 3 Persisted object layout: effective B and compatible q | RustFS backend / paper mechanism | §6; source ledger R01–R05 at fixed RustFS research revision |

Current BrewFS checkout rechecked at `f80e7148c82e9f1ef235ab19318b89cb41a093a2`.
Backend statements remain tied to the existing fixed-revision source ledger;
this illustration does not silently requalify the backend's current branch.

## Edges and their conditions

1. Agent tools issue FUSE requests to their workspace view.
2. The resolver checks/updates private upper state; only upper-permitted
   inheritance follows the packed lower. A whiteout does not fall through.
3. Upper/control requests reach the mutable metadata service. Private payload
   PUT/GET requests reach private objects. These are separate records/bytes.
4. The per-client packed reader requests snapshot objects/ranges directly from
   object storage. Supported lower metadata is in the snapshot; this is not a
   claim that the entire filesystem bypasses the metadata service.
5. The producer builds finalized objects for the selected snapshot. Its PUT
   arrow targets the object-store group; dependencies/publication/GC are not
   expanded into a second lifecycle diagram.
6. Dashed hint edges from finalized private/producer uploads indicate the
   integration that the selected Entity path and producer must complete and
   verify. The client proposes h(Lo); the backend validates B and selects a
   compatible q for eligible writes, persisting the effective layout.
7. Reads, verification and repair interpret the stored layout. The upper
   currently fetches a whole object for its hash check; lower frame reads can
   request ranges. No fixed GET count or acceleration is encoded in the figure.

## Assumptions and bounds

- One workspace pins one lower manifest; ×N means independent clients with
  private uppers that can share S, not an N-agent shared mutable upper (§3).
- Arrows show logical requests/dependencies; response arrows are omitted.
  Solid paths establish source-level structure, not completed runtime proof.
- Dashed has exactly one meaning: hint wiring requiring integration/validation.
  It is not used for client boundaries or normal return traffic (§7).
- B and q are separate persisted quantities. q is geometry/eligibility gated;
  a sent hint does not prove a changed effective layout (§6–7).
- Publication, recovery, whole-object integrity and the experimental fresh-only
  mount limitations remain in the caption/text; the drawing asserts none of
  those as evaluated guarantees (§3–7).

## Composition and editing

7-inch width to match the actual USENIX text block; white background, dark
Arial text, neutral external/storage boxes and one blue accent for the three
paper mechanisms. Three intended text sizes: 10.5, 9 and 8.2 pt. Stable SVG
group IDs map to component/edge names. Text remains live; no bitmap tracing,
outlined labels, AI-generated technical content or external embedded assets.
Two-bend routing is allowed for the long hint dependency to keep it clear of
data labels. This is a deliberate exception to the straight-edge preference.

The existing Overview caption will be rewritten around the final figure,
including the numbered mechanisms, upper-first inheritance, finalized-object
boundary and integration limits. Source checks, font/bounds audits and final
render inspection precede delivery.
