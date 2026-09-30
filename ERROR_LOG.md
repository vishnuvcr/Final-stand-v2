# Error Log

| Error ID | Phase | Severity | Status | Description | Resolution |
|---|---|---|---|---|---|
| E0001 | Bootstrap | info | resolved | GitHub repository was empty; file fetch returned 404. | Initialized repository with control files. |
| E0002 | Phase 1 | info | resolved | Initial run listing did not show the PR workflow immediately after creation. | Added a main-branch runner and verified successful Phase-1 PR execution. |
| E0003 | Phase 2 | warning | resolved | Phase-2 workflow initially lacked a push trigger, so opening the PR did not produce a run. | Added push trigger for phase-2 branch and verified the Phase-2 workflow entered GitHub Actions queue. |

## Rule
Every material data, code, reproducibility, or methodological error encountered during the research is recorded here with its resolution before the phase is closed.
