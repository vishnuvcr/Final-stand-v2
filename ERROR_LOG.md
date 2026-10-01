# Error Log

| Error ID | Phase | Severity | Status | Description | Resolution |
|---|---|---|---|---|---|
| E0001 | Bootstrap | info | resolved | GitHub repository was empty; file fetch returned 404. | Initialized repository with control files. |
| E0002 | Phase 1 | info | resolved | Initial run listing did not show the PR workflow immediately after creation. | Added a main-branch runner and verified successful Phase-1 PR execution. |
| E0003 | Phase 2 | warning | resolved | Phase-2 workflow initially lacked a push trigger, so opening the PR did not produce a run. | Added push trigger for phase-2 branch and verified the Phase-2 workflow entered GitHub Actions queue. |
| E0010 | Phase 6 | blocking | unresolved | The available GitHub connector exposes workflow files and workflow-result inspection but no workflow dispatch/run operation; API commits did not expose an Actions result for the Phase-6 workflow. | Added the Phase-6 workflow plus a temporary main-branch runner and documented the limitation. Artifact-level analysis was completed where possible; full counterfactual option repricing and model ladder execution remain blocked. |
| E0011 | Phase 6 | methodological | resolved | The committed Phase-3 ledger contains realized P&L only for the originally selected Bull/Bear side, so alternative direction models cannot be assigned an opposite-side P&L from that ledger alone. | Do not fabricate counterfactual P&L. Require a runnable rerun of the option-pricing engine that prices both structures before promoting any direction model. |
| E0012 | Phase 6 | modeling | resolved | A heavy-tail MC-only substitution was tested at artifact level and did not improve directional hit rate; confidence filtering did not robustly reduce drawdown. | Do not promote innovation-distribution tuning alone. Prioritize richer conditional features and counterfactual downstream validation. |

## Rule
Every material data, code, reproducibility, or methodological error encountered during the research is recorded here with its resolution before the phase is closed.

| E0013 | Phase 6 | execution | resolved | First full Phase-6 Actions run completed data hydration but failed because counterfactual expiry keys were strings while signal expiry keys were Python date objects, producing an empty merge and a pandas `DataFrame.model` error later in the summary stage. | Store counterfactual expiry keys as date objects and fail early when the counterfactual table or merge is empty. |
| E0014 | Phase 6 | execution | resolved | The first successful code path still required a rerun after E0013; the corrected run completed all model and counterfactual calculations successfully. | Verified GitHub Actions run 13 completed successfully and committed all Phase-6 artifacts. |
