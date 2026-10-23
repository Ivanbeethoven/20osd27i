# Principles rewrite: source scope

Date: 2026-10-23. This audit informed the author's requested rewrite; it is a source inspection, not a runtime qualification.

- Author source: `../ppt-principles/slides.json` and `slides.txt`, extracted from all 24 slides in presentation order with explicit notes relationships. Original PPT SHA-256: `5e3da1e19e11a4665cf2cd9fbc67484e51932b3eb16084b14ed87745fe68a3e5`.
- Current BrewFS source: upstream `main` commit `242af5f7e9bba7afc0c61778f1084fcb20e083a0`, timestamp 2026-10-23T19:12:57+08:00. Read-only export: `../../../brewfs-principles-242af5f` relative to this directory. The source checkout was not changed or reset.
- The delta from the prior inspected `f80e7148c82e9f1ef235ab19318b89cb41a093a2` contains the bandwidth fix in `src/chunk/bandwidth.rs` and review artifacts. The mechanisms audited here were inspected against the exported current revision.
- RustFS evidence is separately fixed to research fork `cc4926fac1107aee76540f28bf22dbd47fcbca24`; it does not establish behavior of the current upstream or every S3 service.
- The historical local worktree named in the PPT was not available on this machine. PPT intent and current source behavior are kept distinct.

## Audit records

- [Workspace views, mutations, publication and recovery](workspaces.md)
- [Packed metadata, lookup, construction and format versions](packed.md)
- [Client granularity, fetch policy and optional backend layout](objects.md)
- [Chinese relationship synthesis](../../planning/03-mechanism-relationships.zh.md)

All numbered manuscript chapters and the abstract were updated. The existing FUSE observation section, bibliography, numeric evaluation budgets and planned experimental status were preserved. Final build and visual checks are recorded in `../../validation/principles-rewrite/` and `../../validation/quality-report.md`.
