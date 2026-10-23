# WOLVES opening-section reading

Read on 2026-10-24 from the official USENIX full paper.

**Title:** Fast and Synchronous Crash Consistency with Metadata Write-Once File System. OSDI 2025.
[Official record](https://www.usenix.org/conference/osdi25/presentation/pan) · [Official PDF](https://www.usenix.org/system/files/osdi25-pan.pdf).

Read all of §1–2, printed pp.859–861 (PDF pp.2–4, counting the cover). Also inspected the transition into §3 and its operation-path diagrams.

**Introduction:** the storage medium enables a stronger durability target; two existing approaches incur different forms of work; measurements identify a shared cost; a new metadata representation addresses that cost; the resulting implementation challenges organize the techniques. Results and contributions then close the argument.

**Background:** define the I/O stack and target semantics, then compare the operations and ordering imposed by existing approaches. A compact comparison prepares the reader for the separate motivation study. Background is not a general survey of file systems.

**Application to BrewFS:** explain what shared-state mechanisms already accomplish before identifying access decisions they leave open. Preserve the distinction between a cost model and measured bottlenecks. WOLVES has causal path measurements and completed performance evaluation; BrewFS's request-count pilot cannot support equivalent claims. Its metadata packages address a different problem from BrewFS's immutable Packed Metadata.
