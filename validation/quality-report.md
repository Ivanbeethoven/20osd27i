# Final quality report

Date: 2026-10-23. Scope: principles rewrite from the author's PPT and a fixed current BrewFS source audit. The three optional mechanisms are view composition, immutable metadata representation/access, and client object formation with optional backend layout. No BrewFS mount, fault-injection, or performance experiments were executed in this revision.

## Manuscript and evidence

- Rewrote the abstract and principles in all ten numbered chapters. The experimental protocol, related work, and conclusion now use the same optional-composition model.
- Preserved `paper/sections/02-agent-observations.tex` byte for byte, including the eight tasks and 1,138,884 FUSE requests. The bibliography and both official style files are unchanged. Every numeric token in the evaluation chapter remains unchanged from the immediately preceding draft.
- BrewFS source is fixed at `242af5f7e9bba7afc0c61778f1084fcb20e083a0`; the backend evidence remains the separate RustFS research fork `cc4926fac1107aee76540f28bf22dbd47fcbca24`. Earlier evidence inventories remain historical, rather than being relabelled as current.
- The PPT was read in presentation order, with explicit slide-to-notes relationships, and its rendered slides were inspected. Current Packed v3 is distinguished from the PPT's earlier tree-and-batch format. Client granularity g is distinguished from backend B/q and from finalized object length.
- Three delegated audits and chapter rewrites were integrated, followed by independent cross-review of mechanism dependencies and object/recovery boundaries. Detailed source evidence is in `evidence/principles-code/`; the Chinese synthesis is `planning/03-mechanism-relationships.zh.md`.

## Artifact verification

| Check | Named draft | Neutral-name preview |
|---|---:|---:|
| Successful XeLaTeX/latexmk build | Yes | Yes |
| Total pages | 17 | 17 |
| Last body page | 15 | 15 |
| Page size | US Letter | US Letter |
| Undefined citations/references | 0 | 0 |
| Overfull boxes / missing glyphs | 0 / 0 | 0 / 0 |
| Embedded fonts | All | All |
| Type 3 fonts | 0 | 0 |
| Text outside page bounds | 0 | 0 |
| Explicit author metadata | Empty | Empty |
| BrewFS/source-revision identity matches in preview text | N/A | 0 |

Both final PDFs were rendered completely with Poppler and visually inspected in contact sheets. Full-page checks covered the mechanism-selection table, architecture composition, granularity example, and mount-entry table. The mount table was adjusted to avoid stretched labels and rechecked after rebuilding. No clipped text, overlapping figures, or broken formulas were found. Underfull justification diagnostics remain (53 named, 57 preview); they were visually reviewed and do not represent overflow.

The architecture artwork is unchanged. Its caption now explicitly scopes it to an illustrative combination, with alternatives and the preceding client g boundary explained in the text. The original packed-access figure remains one representative lookup, not a fixed request-count claim.

`validation/principles-rewrite/pdf-inspection.json` records PDF hashes, fonts, metadata, and preservation checks. The final package validator passed: 29 bibliography entries, 27 cited entries, all seven RQs, exactly 17 experiments E00–E16, and all experiment statuses still planned. `git diff --check` passed. Source edits did not change the official USENIX style, margins, or type sizes.

## Remaining scope

Architectural optionality does not establish every factor combination as a runnable mode. Section 7 records concrete entry points, fixed g configuration, independent backend gates, missing hint connections, and supported recovery scopes. No online access-adaptive client block controller or end-to-end worker migration is claimed. Both PDFs remain internal working drafts; the body has 15 pages and has not been reduced to the recorded submission budget. The neutral-name PDF is a preview, not certification of full submission anonymity.

The prior quality report is retained in `validation/principles-rewrite/quality-before.md`; earlier figure and workload reviews remain in their original validation directories.
