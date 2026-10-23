# Opening-section reading: Oxbow and Okapi

Read on 2026-10-24. Sources are official USENIX full papers. The PDF page numbers below count the USENIX cover as page 1. These notes describe argument structure, not reusable prose or evidence about BrewFS performance.

## Oxbow (OSDI 2026)

**Exact title:** Oxbow: A Coordinated Architecture for Multi-Component File Systems.

[Official record](https://www.usenix.org/conference/osdi26/presentation/kim-jongyul) · [Official PDF](https://www.usenix.org/system/files/osdi26-kim-jongyul.pdf).

Read §1 Introduction and all of §2 Trends in Modern Storage Systems: printed pp. 1425–1427, PDF pp. 2–4.

**Introduction progression:** hardware change → limits shared by competing placements → coordination as the central idea → three coordination problems paired with mechanisms → implementation and measured results. The mechanisms appear only after the reader understands why placement alone cannot satisfy the requirements.

**Background progression:** architecture taxonomy → benefits and forfeited services of user-level I/O → CPU evidence and offload constraints → explicit requirements. The CPU observation distinguishes throughput from resource consumption; weaker device processors constrain which work should move.

**Transferable rules:** (1) Identify the common cause before naming components. (2) Make each background subsection produce a requirement or constraint used later. (3) Describe the new costs introduced by composition, then explain the mechanism that controls each cost. Oxbow's measurements establish its own trade-offs; they do not establish BrewFS's performance.

## Okapi (OSDI 2025)

**Exact title:** Okapi: Decoupling Data Striping and Redundancy Grouping in Cluster File Systems.

[Official record](https://www.usenix.org/conference/osdi25/presentation/athlur) · [Official PDF](https://www.usenix.org/system/files/osdi25-athlur.pdf).

Read §1 Introduction, §2 Striping and grouping in cluster storage, and §3 Why decouple striping from grouping?: printed pp. 897–900, PDF pp. 2–5. The browser PDF extractor timed out on re-opening; the official PDF was downloaded temporarily and the complete relevant pages were extracted locally.

**Introduction progression:** minimum storage vocabulary → the exact coupled decisions → two resulting costs → situations where the decisions want different settings → decoupling → implementation challenges and solutions → implementation, evidence, contributions.

**Background progression:** define striping and grouping separately, including the resources each controls; then use a numerical access example and workload/transition observations to show why equal settings can be undesirable. Background explains the mechanism of the problem before introducing the design.

**Transferable rules:** (1) Define the unit and decision at each layer before comparing settings. (2) Ground independent configuration in different workload pressures, not in flexibility as a benefit by itself. (3) Separate semantic compatibility from the engineering cost of implementing the combinations. Okapi's production observations and measured gains cannot serve as BrewFS evidence.

## Diagnosis of the current BrewFS opening (author manuscript, not source summary)

The current introduction leads too quickly with configuration distinctions and optionality. Its latter paragraphs read like experiment-control instructions and an implementation audit, while the reader still lacks a concrete account of the system's problem. The background similarly opens with the generic FUSE path and repeatedly tells the reader what cannot be inferred. These are valid boundaries, but they interrupt the motivation.

Use one running setting: several isolated agent attempts start from a stable repository environment, traverse metadata, and access limited file ranges. Explain separately the cost of provisioning each view, obtaining immutable metadata, and turning requested ranges into storage work. Establish the shared question—how to avoid paying for unrelated state at each boundary—before introducing the three independently selectable mechanisms. State optionality once, with one useful independent-use example. Keep the existing empirical scope explicit in one compact sentence; retain detailed controls and current path restrictions in the later sections that already own them.

The draft's eight runs support statements about observed file-operation structure. They do not establish cross-task state overlap, backend amplification, scaling, or end-to-end BrewFS speedup. A running example should be marked as explanatory rather than presented as a measurement.
