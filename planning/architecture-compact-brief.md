# Compact methods figure: author-requested revision

The user requests a compact OSDI-style architecture that exposes the technical
method. This revises the already authorized architecture brief; no new runtime
claim or component is introduced. Target: 504 x 230 pt at full two-column width,
8 pt minimum live text, flat boxes, sparse color, no repeated client illustrations.

## Visual argument

One workspace keeps private namespace state and explicit byte mappings while
referencing a pinned shared snapshot. Packed indexes locate metadata and
authenticated payloads. The backend persists an admitted per-object layout;
the application request, packed frame and physical verification/read quantum are
different boundaries. Three aligned panels expose those mechanisms.

1. Delta-based workspace: name resolution (present / hidden / absent and visible),
   explicit LowerRange / Data / Hole map, a private payload reference, durable
   PUT before publishing a map. Mutable metadata is outside snapshot objects.
2. Shared snapshot: pinned manifest roots, a paged directory-name index, GroupMeta with name,
   attributes and locator, then a frame descriptor and authenticated payload.
   LowerRange points into the lower read path; the name fallback uses its index.
3. Object layout: finalized upload length, a dashed B hint h(L_o) integration edge,
   backend admission and compatible q selection, persisted B/q/d/p, and schematic
   data/parity shards subdivided into q cells. The 2+2 drawing is illustrative.

Solid arrows show logical references/access dependencies, not a universal
execution order or a fixed GET count. The dashed arrow has one meaning: hint
wiring requires integration in the selected paths. The private object and
snapshot object upload pipelines are summarized once by finalized upload length;
they are not separate synchronization dependencies. Each workspace has its own
reader; repeated clients and producer internals are omitted.

## Primary-paper visual references

Inspected original PDFs on 2026-10-23, including actual rendered pages:

- Oxbow, OSDI 2026, Figures 3, 5 and 6 (PDF pages 5 and 7): components are
  distinguished by ownership; read/write paths carry explicit steps in compact
  single-column figures. https://www.usenix.org/system/files/osdi26-kim-jongyul.pdf
- DeLFS, OSDI 2026, Figure 3 (PDF page 5): representation and on-storage layout
  are shown together, with connections between fields and their storage regions.
  https://www.usenix.org/system/files/osdi26-ahn.pdf
- WOLVES, OSDI 2025, Figures 3 and 5 (PDF pages 6 and 8): small field records
  explain the mechanism; repeated CPU roles are compressed and the layout is
  visible. https://www.usenix.org/system/files/osdi25-pan.pdf
- SquirrelFS, OSDI 2024, Figure 2 (PDF page 6): explicit states and edges explain
  a protocol rather than decorating component names.
  https://www.usenix.org/system/files/osdi24-leblanc.pdf

These are design references, not journal-mandated templates. No figure artwork
or experimental data was copied. Downloaded reference PDFs and renders are
outside the repository in outputs/osdi-figure-reference/.

## Evidence and assumptions

- Entity current-state semantics: paper sections 3-4, source_evidence.md, and
  local source f80e7148c82e9f1ef235ab19318b89cb41a093a2 under
  src/workspace_overlay/entity/model.rs and data.rs. Explicit-map absence is not
  automatic inheritance; whiteout and opacity are represented by 'hidden'.
- Packed path: sections 3 and 5 and source_evidence.md; name and inode queries
  are distinct index routes, GroupMeta is a representative name route, and
  a LowerRange read is not forced through a new name lookup.
- Backend: section 6 and the pinned RustFS source evidence. For an eligible
  full stripe s=B/d, q divides s and qd divides B. The schematic uses d=p=2
  and s=2q, consistent with the 64 KiB / 16 KiB selector example in section 6;
  it does not assert that all objects have this geometry. Smaller-q writes remain gated.
- Entity upper full-object verification is retained in the figure and caption.
- No inference of measured sparse updates, sharing gains, optimal q, constant
  GET counts or end-to-end integrated qualification is permitted.

The editable generator is tools/draw_architecture_compact.py. SVG component
groups have stable IDs. Audit the SVG and PDF and inspect final manuscript size.
