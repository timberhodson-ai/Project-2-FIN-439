# Capstone — ADP screening and ETF paper pilot

AI use: OpenAI Codex reused the existing portfolio app and added the ADP eligibility screen and automated checks. The student is responsible for verifying the analysis and approving the committee decision.

This is for education only and does not constitute investment advice.

## Run the app

From this folder, install dependencies using Python 3.14:

```sh
python -m pip install -r requirements.txt
```

Launch the app and open the local URL printed in the terminal:

```sh
python -m streamlit run app.py
```

The default ADP reference price is $288.90. The app reads the saved October 16 Project 1 DCF to compute the maximum price for admitting ADP to further paper-position risk testing. The existing Project 2 engine runs the ETF paper pilot at 0% live capital. The bundled snapshots support reproducible scenario analysis without data credentials. The ADP reference price is historical, and the ETF optimizer does not estimate ADP's risk contribution.

Reused evidence: [Project 1 ADP valuation](docs/ADP_project_DCF.md), [Project 2 ETF signal data card](docs/data-card.md), and the Project 2 portfolio engine in `analysis.py` and `portfolio.py`.

## AI evidence review

Set `GENAI_API_KEY` and `GENAI_MODEL` as environment variables in the terminal that launches Streamlit. Use a key from your Purdue GenAI Studio account and a model ID available to that account. Keep the real key outside the repository. [RCAC API setup](https://docs.rcac.purdue.edu/services/genai/api/)

Use **Request evidence review** to ask the model to prioritize a diligence gap. The app checks the response format and source ID. The analyst compares the proposed check with the evidence and records an acceptance or correction with a reason. ADP can advance to paper-position risk testing only after clearing the valuation screen and completing the review under a viable ETF pilot. If the API fails, use the manual route and preserve the exact prompt, raw model output, and your validation. See [validation and AI use](docs/validation-and-ai-use.md).
