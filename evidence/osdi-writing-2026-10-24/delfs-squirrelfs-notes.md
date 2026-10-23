# OSDI opening-section reading notes

Read on 2026-10-24. These are structural observations from the published papers, not an official OSDI writing template. Official USENIX PDFs were opened and the relevant prose read, rather than relying on abstracts. PDF-page numbers below include the proceedings cover sheet.

## DeLFS (OSDI 2026)

**Title:** *DeLFS: A Decentralized Log-Structured File System for Manycores*.
[Official record](https://www.usenix.org/conference/osdi26/presentation/ahn); [official PDF](https://www.usenix.org/system/files/osdi26-ahn.pdf).
Read §1–§2, printed pp. 793–794 (PDF pp. 2–3), plus the diagnostic §3, pp. 794–795 (PDF pp. 3–4).

Introduction progression: (1) useful property of LFS, then a specific multicore limitation; (2) Figure 1 establishes the scaling gap against device throughput and shows why a page-cache improvement is insufficient; (3) prior approaches identify the remaining scope; (4) one central idea—distributing resource and lock ownership—organizes three techniques; (5) implementation and evaluation substantiate the proposed solution.

Background is only one paragraph: enough LFS/F2FS organization to understand centralized coordination. Measurements and successive bottleneck removal occupy a separate analysis section. Definitions prepare the diagnosis; experiments identify the bottleneck; design addresses that diagnosis.

Transferable rule: introduce a concrete unresolved cost before naming mechanisms, and connect each mechanism to its cause. Do not mechanically copy the three-technique sequence: DeLFS explicitly makes resource partitioning foundational to its locking design, whereas BrewFS's three capabilities have independent deployment roles. Its measured performance conclusion cannot be imitated with planned experiments.

## SquirrelFS (OSDI 2024)

**Title:** *SquirrelFS: using the Rust compiler to check file-system crash consistency*.
[Official record](https://www.usenix.org/conference/osdi24/presentation/leblanc); [official PDF](https://www.usenix.org/system/files/osdi24-leblanc.pdf).
Read §1, printed pp. 387–389 (PDF pp. 2–4), and §2, pp. 389–390 (PDF pp. 4–5).

Introduction progression: (1) important correctness property; (2) testing and verification expose different costs, summarized in Table 1; (3) a precise intermediate goal; (4) Rust ordering checks offer an opportunity, but require suitable invariants; (5) persistent memory makes synchronous soft updates feasible; (6) an inode example illustrates the mechanism; (7) implementation, evaluation, guarantee boundaries, and contributions establish the resulting position.

Background separates the problem from the opportunity. Crash-consistency definitions and prior proof burdens explain the gap. A short erroneous file-creation example then makes the typestate requirement inspectable. The persistent-memory argument explains why the classical mechanism can be simplified. The example explains a constraint; it is not presented as performance evidence.

Transferable rule: make the key abstraction tangible with one example and explain the enabling condition. State limitations near the claim they qualify. Do not copy its length or its tightly dependent two-idea construction: independent BrewFS options require a different relationship, and Rust alone does not establish its guarantees.

## Diagnosis of the current BrewFS opening

This diagnosis is based on the current local `sections/01-introduction.tex` and `sections/02-motivation.tex`, not on claims in the papers above.

- The first paragraph rapidly moves from agent file operations to an abstract three-way distinction. It does not yet make the reader inhabit a concrete repeated-task execution or identify the cost that persists after sharing a baseline.
- The second paragraph lists several plausible costs but does not distinguish those directly observed in the available traces from analytical tradeoffs. This blurs motivation and hypothesis.
- Mechanism names appear before a clear account of why ordinary object-backed file access does not resolve the motivating workload. The subsequent composition paragraph mixes mechanisms, negative interactions, and selection advice.
- The final two introduction paragraphs read as an implementation-audit/research-protocol report. The constraints are honest and necessary, but much of their detail belongs in implementation and evaluation. The opening still needs a concise affirmative account of the actual design contribution, followed by one bounded evidence sentence.
- Background defines many boundaries accurately, yet spends substantial space on fairness instructions and cautions. These should become a small number of concrete concepts and an example that the design subsequently uses; benchmarking controls should remain in evaluation.
- Preserve the key correction already achieved: shared views, immutable metadata representation, and object layout are independent decisions. A generic three-challenge/three-technique rhetorical pattern must not recreate a mandatory pipeline.

## Suggested local writing rules

1. Begin with one concrete execution pattern and the filesystem work it induces; introduce abstract distinctions after the reader can picture that work.
2. Give every introduction paragraph one argumentative job: setting, unresolved cost, observation, design idea, mechanism role, or evidence boundary.
3. Associate each proposed mechanism with one specific cost and its applicability condition. Explain optionality once through independent roles and concrete valid uses.
4. Separate supplied observations, illustrative calculations, implemented behavior, and hypotheses in the prose. None can substitute for a completed performance experiment.
5. Use Background to teach only concepts needed to follow the design. Reserve experiment controls, unsupported combinations, and wiring details for their respective sections.
6. Use one compact example to distinguish view composition, metadata access, and payload access; keep metadata requests distinct from FUSE requests and physical bytes.
7. End the introduction with concrete delivered contributions and the actual evidence scope. Avoid both unmeasured speedups and presenting the entire paper primarily as an audit protocol.
