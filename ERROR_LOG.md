# Error Log

| Error ID | Phase | Severity | Status | Description | Resolution |
|---|---|---|---|---|---|
| E0001 | Bootstrap | info | resolved | GitHub repository was empty; file fetch returned 404. | Initialized repository with control files. |
| E0002 | Phase 1 | info | resolved | Initial run listing did not show the PR workflow immediately after creation. | Added a main-branch runner and verified successful Phase-1 PR execution. |
| E0003 | Phase 2 | warning | resolved | Phase-2 workflow initially lacked a push trigger, so opening the PR did not produce a run. | Added push trigger for phase-2 branch and verified the Phase-2 workflow entered GitHub Actions queue. |
| E0010 | Phase 6 | blocking | resolved | At one point the available connector did not expose a reliable workflow-dispatch operation, which blocked the full Phase-6 run. | A push-triggered GitHub Actions path was used successfully; the corrected Phase-6 workflow completed counterfactual pricing and the full model ladder. The temporary blocker is retained here as historical provenance. |
| E0011 | Phase 6 | methodological | resolved | The committed Phase-3 ledger contains realized P&L only for the originally selected Bull/Bear side, so alternative direction models cannot be assigned an opposite-side P&L from that ledger alone. | Do not fabricate counterfactual P&L. Require a runnable rerun of the option-pricing engine that prices both structures before promoting any direction model. |
| E0012 | Phase 6 | modeling | resolved | A heavy-tail MC-only substitution was tested at artifact level and did not improve directional hit rate; confidence filtering did not robustly reduce drawdown. | Do not promote innovation-distribution tuning alone. Prioritize richer conditional features and counterfactual downstream validation. |

## Rule
Every material data, code, reproducibility, or methodological error encountered during the research is recorded here with its resolution before the phase is closed.

| E0013 | Phase 6 | execution | resolved | First full Phase-6 Actions run completed data hydration but failed because counterfactual expiry keys were strings while signal expiry keys were Python date objects, producing an empty merge and a pandas `DataFrame.model` error later in the summary stage. | Store counterfactual expiry keys as date objects and fail early when the counterfactual table or merge is empty. |
| E0014 | Phase 6 | execution | resolved | The first successful code path still required a rerun after E0013; the corrected run completed all model and counterfactual calculations successfully. | Verified the final corrected GitHub Actions execution (run 18 / run id 36816076027) completed successfully and committed all Phase-6 artifacts. |


| E0015 | Repository control | resolved | A stale README and error-log status from the earlier partial Phase-6 execution remained after the later successful run. | Reconciled README, research log and error log with the final Phase-6 execution and froze Phase 7 as a separate restart gate. |

| E0016 | Phase 7 | execution | resolved | The Phase-7 data acquisition and non-evaluative feature build completed, but the Actions artifact commit was rejected as non-fast-forward because the branch had advanced while the run was executing. | Hardened the Phase-7 workflow to fetch/rebase the current branch and retry the push up to three times. The failed run is retained as provenance; no research result was used from the failed commit step. |

| E0017 | Phase 7 | execution | resolved | The first option-surface builder commit contained an unclosed per-file `try` block, causing a Python SyntaxError before any feature calculation. | Added the missing exception handler and retained per-date parser errors in `option_surface_errors.csv`; no model or OOS evaluation ran. |

| E0018 | Phase 7 | data acquisition | resolved | The initial option acquisition used an unsupported `nse-data get derivatives equity optidx` path, leaving only missing markers and producing zero option-surface rows. | Switched to the documented `nse-data derivatives --type optidx --date` interface and require an actual CSV before marking a date acquired. |

| E0019 | Phase 7 | data acquisition | resolved | The second `nse-data` option acquisition path still yielded no usable `optidx` files, so the feature builder correctly stopped with zero rows. | Replaced the CLI acquisition with the `nse` package's session-aware `download_document` against the official NSE archive URL, with a legacy-host fallback and explicit target-file validation. |

| E0020 | Phase 7 | source coverage | resolved | NSE historical `optidx` archive access produced no usable files after CLI and session-aware archive attempts, despite successful VIX and equity-report acquisition. | Removed repeated NSE option retries from the main workflow, retained NSE as the canonical attempted source, and locked the reproducible Hugging Face NIFTY option archive as the historical secondary source for option-surface construction. Source provenance is recorded in the option artifacts. |

| E0021 | Phase 7 | execution | resolved | HF option timestamps carried an Asia/Kolkata timezone while the feature cutoff was timezone-naive, causing a pandas invalid datetime comparison. | Normalize option timestamps to Asia/Kolkata and then remove timezone information before applying the fixed 15:30 IST cutoff. |

| E0021 | Phase 7 | feature construction | resolved | HF option timestamps are timezone-aware IST values, while the first builder comparison used naive timestamps and raised a pandas invalid-comparison error. | Standardized signal cutoff comparisons to `Asia/Kolkata` timezone-aware timestamps. No feature or performance result was generated before the fix. |

| E0022 | Phase 7 | execution | resolved | NSE India VIX parquet uses `EOD_TIMESTAMP` and `EOD_CLOSE_INDEX_VAL` rather than the generic date/close names assumed by the first feature builder. | Added the actual NSE schema aliases and retained the source columns as the canonical VIX inputs. |

| E0022 | Phase 7 | feature construction | resolved | NSE India VIX data uses `EOD_TIMESTAMP` and `EOD_CLOSE_INDEX_VAL`, which were not included in the initial schema aliases. | Added the actual NSE column names to the parser; no downstream performance analysis ran before the fix. |

| E0023 | Phase 7 | data coverage | resolved | NSE daily PR report acquisition yielded no parseable breadth rows, causing the feature builder to crash while sorting an empty DataFrame. | Changed the builder to preserve an explicit `unavailable_no_daily_pr_rows` breadth status and continue with FII/DII and corporate-action features; no imputation is performed. |

| E0023 | Phase 7 | execution | resolved | NSE PR-report acquisition produced no parseable breadth rows, causing an empty dataframe to fail at `sort_values`. | Treat empty breadth acquisition as an explicit missing-data condition; the output remains timestamped and coverage reports zero breadth rows instead of inventing values. |
