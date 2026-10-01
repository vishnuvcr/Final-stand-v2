# Research Log

| Step | Phase | Status | Date | Notes |
|---|---|---|---|---|
| 0.1 | Bootstrap | complete | 2026-10-01 | Repository was empty; initialized research control files. |
| 1.1 | Phase 1 | started | 2026-10-01 | User strategy specification captured. Public data-source scan started. |

## Conversation record
### 2026-10-01 — User request
Test a NIFTY weekly options strategy where a Monte Carlo forecast is generated after the previous expiry close, then a directional three-leg OTM4/OTM5/OTM6 structure is entered at 4 DTE 10:00 and exited at expiry.


| 5.2 | Phase 6 | proposed | 2026-10-01 | User clarified that the goal of the direction layer is primarily to reduce large losses/drawdowns and raise trade win rate while retaining the option payoff buffer. Proposed a hybrid regime + ML + conditional Monte Carlo direction engine; not yet executed. |
