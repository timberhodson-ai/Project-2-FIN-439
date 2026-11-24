# Validation and AI use

OpenAI Codex integrated the Lab 15 engine and saved prices into a dedicated Project 2 app, added verdicts and sensitivity checks, and drafted the Lab 20 package on November 17, 2026. The published analysis uses the October 22, 2026 snapshot. The student should review the assumptions and approve the recommendation before submission.

## Validation evidence

The [executed output](visible-output.md) shows two transparent baselines, the VOO benchmark, and the constrained allocation under the same hard rules. The four separate stresses vary a return estimate, the window, annual costs, and the EEM cap. The base reproduces the prior Lab 15 allocation. Direct the committee to the rule-level verdicts and the largest absolute sleeve change, rather than comparing returns alone.

On November 17, 2026, an automated Streamlit check loaded the default screen, verified both baseline failures and the 70% VOO allocation, and flipped the 36-month control to verify the move to 80% VOO. Calculation checks also confirmed the 10-point maximum stress shift and the +2.66% signal. The independent partner cold run is pending.

Proposed assumptions to review: 100% VOO as comparison benchmark, a 0 bp replication base with a 50 bp annual cost stress, a 15 percentage point stop threshold, and a paper pilot with 0% live exposure. The case for the paper pilot relies on limited historical estimates and should be revisited with out-of-sample evidence and a trading-cost estimate. The [data card](data-card.md) documents the source and timing boundary.

On November 23, 2026, OpenAI Codex updated the Streamlit presentation to show rule-level verdicts, the four reference stresses, the committee decision, and the signal's availability boundary. Streamlit AppTest using the pinned dependencies verified the default 70% VOO mix, both baseline failures, all four stress rows, the +2.66% signal, the 36-month move to 80% VOO, a 10.28% return estimate at 250 bp annual cost, and the infeasibility alert at 2,000 bp. The generated Markdown matched the saved executed output exactly. These were automated checks.

## Locked Changed-Input Record — pending student completion

With AI closed, select one input and fill in the prediction fields before running it. Commit and push the prediction alone, then run the chosen change and add the results and explanation in a later commit.

| Record | Student entry |
|---|---|
| Input, old value, new value, and units | Pending |
| Predicted direction of net return, volatility or weights | Pending |
| Predicted effect on mandate verdict and decision | Pending |
| Prediction commit URL | Pending |
| Before-output location | Pending |
| After-output location and results commit URL | Pending |
| Actual effect on decision and explanation | Pending |

## Additional changed-input test

**Prediction written before the run with Codex assistance.** Increase annual portfolio cost from 0 to 250 basis points (2.50 percentage points). With the same estimated risks and enough return above the hurdle, I expect the allocation to stay at 70% VOO and 30% EEM. I expect the net return estimate to fall from 12.78% to 10.28%, volatility to stay at 14.99%, and the mandate to pass. The paper pilot should continue with 0% live capital.

The prediction was written locally before executing this test. There is no pre-run GitHub commit for this run. A new run would be needed to document a GitHub precommit.

| Measure | Before | After |
|---|---:|---:|
| Annual portfolio cost | 0 bp | 250 bp |
| VOO / QQQ / VB / EEM | 70% / 0% / 0% / 30% | 70% / 0% / 0% / 30% |
| Net return estimate | 12.78% | 10.28% |
| Estimated annual volatility | 14.99% | 14.99% |
| Mandate verdict | Pass | Pass |

The results matched the prediction. The uniform cost subtracts 2.50 percentage points from the annual return estimate without changing covariance. The original minimum-volatility mix still clears the 7% hurdle, so it remains the selected portfolio. The largest sleeve move is 0 percentage points. Continue the paper pilot with 0% live capital.

Reproduce in the app by setting **Annual portfolio cost (basis points)** to `250` with the other controls at their defaults.
