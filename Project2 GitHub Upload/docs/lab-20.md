# Lab 20 — Project 2 Readiness

## D — Define

Can a committee member reach the Project 2 decision from the repository alone, and does it survive a precommitted input change? The prior Lab 15 choice supplies the reference allocation of 70% VOO and 30% EEM. This checkout tests whether the process is suitable for a paper pilot and when to stop it.

## R — Review

Use the [manifest](manifest.md) to find the app, instructions, visible results, decision memo, validation record, and outstanding video links. No Week 12 must-fix list was present in the available files. The integration addressed three observable gaps: the old app opened on a training case, the ETF baselines lacked rule-level verdicts, and the rate/vintage lab had no timing rule connected to this ETF snapshot.

## I — Implement and cold run

No class partner was available. Codex simulated the partner checkout from a fresh local copy with dependencies already installed.

| Partner record | Entry |
|---|---|
| Repository revision and date | Local Project 2 snapshot, November 17, 2026 |
| Command run | `python -m streamlit run app.py` using the installed Python executable |
| First failure, or none | Server started. The first automated UI check timed out at its 3-second limit. Increasing the test harness timeout allowed verification without an app change. |
| Elapsed time | 3.3 seconds to first result and 3.7 seconds through the control rerun in the clean-copy UI test. Dependency installation was outside the timing. |
| Where the result appeared | Main app table, Constrained row. The recommendation appears below the table. |
| App control changed and mandate verdict | Annual portfolio cost 0 to 250 bp. Net return estimate 12.78% to 10.28%, mandate PASS, paper pilot continues. |

## V — Validate

The [validation record](validation-and-ai-use.md) holds the student's AI-off prediction, commit link, and before/after evidence. The standard engineering stress cases are documented separately from that exercise. The student chooses and predicts their own change with AI closed, commits and pushes the prediction, then runs the change and records its effect.

The validation record also contains a completed local cost test. Raising annual cost from 0 to 250 basis points lowered the net estimate from 12.78% to 10.28%. The 70% VOO / 30% EEM mix still passed, and the paper-pilot recommendation held. The pre-run GitHub commit remains pending.

**Code explanation completed (student reported).** Simulated follow-up question: Why did cost lower the estimated return without changing the weights? `analysis.run()` subtracts the same annual cost from every sleeve's return estimate. The covariance still comes from the same volatilities and correlations. `portfolio.search_mix()` tests the return hurdle before selecting the feasible mix with the lowest volatility. The original mix still clears the hurdle, so it remains the answer.

## E — Execute one fix

**No app fix needed.** The simulated rerun completed with a longer test-harness timeout.

**Decision line for student approval** — Pilot the process on paper with 0% live capital and stop if a stress makes the 7% hurdle infeasible under the mandate or moves any sleeve by at least 15 percentage points.

## R — Reflect

The clean-copy run we performed showed that someone following the README could find the starting allocation and see whether it passed the portfolio rules. The cost test helped me understand that a lower estimated return can leave the allocation unchanged when the portfolio still clears the 7% hurdle. Before the deadline, I’ll leave the ETF universe and portfolio rules alone so my app, memo, and published results stay consistent.

## GitHub checkout

Repository and individual submission URLs are pending. See [manifest](manifest.md) for the files to link. [Course Lab 20 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-13/lab-20-project2-readiness.md)
