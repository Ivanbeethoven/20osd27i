# Venue rules and systems-paper structure

## Scope

This dated working reference was checked on 2026-10-22. The author did not select a cycle; OSDI 2027 is the nearest published CFP used for planning. Reopen official pages for future use.

## OSDI 2027 rules

Sources: [CFP](https://www.usenix.org/conference/osdi27/call-for-papers), [author requirements](https://www.usenix.org/conference/osdi27/requirements-authors), [USENIX templates](https://www.usenix.org/conferences/author-resources/paper-templates).

- Research submissions: at most 12 pages including figures/tables; references may extend beyond this limit. Extra appendix pages cannot extend the main PDF. The CFP separately permits optional supplemental files that reviewers need not read.
- US letter, two columns, 10-point Times or similar type, 12-point leading, 7 × 9 inch text area, 0.33 inch column gap. Number pages and ensure grayscale legibility.
- Double-blind review: remove author/institution identifiers and acknowledgments. For public projects, use a different anonymized project/system name.
- The CFP permits 14 content pages for accepted papers, not initial submissions.
- Abstract: 2026-12-01 22:59 UTC / 2026-12-02 06:59 Asia/Shanghai. Paper: 2026-12-08 22:59 UTC / 2026-12-09 06:59 Asia/Shanghai. These dates are not scheduling instructions.
- Wholly or largely AI-generated submissions are prohibited; AI editing is permitted. Internal assistance does not establish submission eligibility.
- A possible preliminary review stage is not confirmed in the accessed CFP. Recheck before submission.

No detailed 2027 artifact-evaluation schedule or badge promise was found in the accessed CFP. The [2026 artifact call](https://www.usenix.org/conference/osdi26/call-for-artifacts) can guide preparation, not replace 2027 rules.

## Lessons from actual papers

These are interpretations of argument structure, not compulsory templates.

### Assise, OSDI 2020

[Paper page](https://www.usenix.org/conference/osdi20/presentation/anderson); [PDF](https://www.usenix.org/system/files/osdi20-anderson.pdf). Inspect §2.2, §3, and §5. A changed hardware cost hierarchy motivates storage placement and coherence choices. Evaluation separates latency sources, applications, availability, and scaling, with explicit discussion of replication and consistency differences between baselines. State comparable guarantees and placement choices before interpreting speedups.

### SquirrelFS, OSDI 2024

[Paper page](https://www.usenix.org/conference/osdi24/presentation/leblanc); [PDF](https://www.usenix.org/system/files/osdi24-leblanc.pdf). Inspect §2, §3.5, and §5. A specific correctness burden motivates an enforceable ordering discipline. The paper names what the compiler can and cannot establish; evaluation covers performance, recovery, resource use, and correctness. Make the boundary of a guarantee explicit rather than using a broad “verified” label.

### WOLVES, OSDI 2025

[Paper page](https://www.usenix.org/conference/osdi25/presentation/pan); [PDF](https://www.usenix.org/system/files/osdi25-pan.pdf). Inspect §3, §4, and §6. Metadata I/O cost decomposition leads to a changed representation. Evaluation tests crash behavior, throughput, aging, recovery, and resources. Construct an explicit evidence chain between baseline costs and representation choices, using original measurements rather than another system's findings.

## Flexible 12-page budget

This is an allocation aid, not a venue rule.

| Content | Pages |
|---|---:|
| Title, abstract, introduction | 1.5 |
| Background, motivation, model | 1.5 |
| Mechanisms and shared invariants | 3.5 |
| Implementation and limitations | 0.75 |
| Evaluation | 3.75 |
| Related work and conclusion | 1.0 |

Move related work earlier when needed for the gap. Reserve space for correctness and negative results. A planning manuscript need not fill twelve pages.
