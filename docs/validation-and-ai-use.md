# Validation and AI use

OpenAI Codex helped integrate the Project 1 ADP DCF and Project 2 ETF dashboard, implement the Purdue GenAI review and output guard, and draft documentation. The two saved evidence dates are October 16, 2026 for the ADP valuation and October 22, 2026 for the ETF analysis. See the [DCF](ADP_project_DCF.md) and [ETF signal data card](data-card.md) for limitations and provenance.

## AI evidence review

`pilot_review.py` holds the exact prompt, API request, and response validation. The guard requires two JSON fields, a known evidence ID, and a bounded text check. An analyst reviews whether the check follows from the cited evidence and records a reason before ADP can advance.

Live Purdue GenAI Studio API run on November 23, 2026, using the configured `gpt-oss:120b` model ID and the exact `PROMPT` in `pilot_review.py`. The app accepted the response structure and the supplied `terminal` evidence ID. The user reported this raw response:

```json
{
  "evidence_id": "terminal",
  "check": "Perform a sensitivity analysis of the terminal growth rate and terminal multiple used in the DCF to quantify how variations affect the estimated enterprise value for ADP."
}
```

**Analyst disposition (student wording, with spelling corrected).** I’d keep the suggestion to check terminal growth because terminal value accounts for 74.6% of ADP’s base-case enterprise value. I’d correct the suggestion to vary a terminal multiple because our DCF uses perpetual growth and has no exit multiple. I’d use our existing WACC and perpetual-growth table to see whether the valuation changes enough to reconsider ADP for the paper pilot. This large percentage of terminal value within the assessment of the company builds too large of a reliance on distant cash flows, so I feel it is necessary to do the latter.

**Follow-up check (Codex-assisted).** The [ADP DCF](ADP_project_DCF.md) reports $243.71 per share in the highest-value cell of its WACC and perpetual-growth grid. Even that value is below the $288.90 reference close before applying any margin-of-safety discount. The saved grid therefore leaves the ETF-only paper-pilot decision intact. The grid reports equity value per share, the measure used for the price screen.

## Cross-component test — missing ADP valuation input

On November 23, 2026, a Streamlit AppTest simulated `FileNotFoundError` when the app tried to read `ADP_project_DCF.json`. The expected result was to hold ADP out and independently evaluate the ETF portfolio using its intact input data. The app displayed the unavailable-valuation error, held ADP out, retained the ETF paper-pilot header, and reported `PASS` for the constrained ETF portfolio. A separate synthetic response with an unknown AI evidence ID was blocked by the guard. These automated checks are separate from the student-authored locked record and the real model interaction.

## Locked Changed-Input Record — AI-OFF Test

The student reports that the professor permitted this scenario to be used for the required record. The student supplied the prediction in chat before Codex ran the test on November 23, 2026. AI assistance was used in discussing the screen and running the test. A pre-run GitHub commit has not been verified.

**Student prediction, verbatim.** “My new estimate for share price is $120 dollars per share and this will include ADP iwth the client test because it now meets the requirement for the upper bound limit of about $142/ share.”

Codex ran the Streamlit app with the default ETF inputs and changed only the hypothetical ADP scenario price. The DCF-based ceiling remained $142.60 per share.

| Result | Before | After |
|---|---|---|
| ADP scenario price | $288.90 per share | $120.00 per share |
| ADP valuation screen | Fails | Clears; evidence review required before advancing |
| Direct ADP paper weight | 0% | 0% |
| ETF decision and constrained mix | Pilot on paper, 70% VOO and 30% EEM | Pilot on paper, 70% VOO and 30% EEM |

The eligibility result matched the prediction. The automated check also confirmed the full ETF comparison was identical before and after. This run recorded the valuation decision only; the evidence review and ADP position-risk test are separate steps.
