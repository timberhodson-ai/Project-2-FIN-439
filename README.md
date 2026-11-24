# Project 2 — ETF allocation under a 7% hurdle

AI use: OpenAI Codex helped integrate the prior labs, run checks, and draft documentation. The student is responsible for verifying the analysis and approving the committee decision.

This is an educational exercise, not investment advice.

## Run the app

The investment committee is evaluating a paper pilot for a long-only ETF allocation. The app compares the mandate verdicts, shows four reference stresses, and lets the committee test its own assumptions against the frozen October 22, 2026 snapshot.

From this directory, install the dependencies once using Python 3.14:

```sh
python -m pip install -r requirements.txt
```

Launch the app:

```sh
python -m streamlit run app.py
```

Open the local URL printed in the terminal. To reproduce the reference window stress, check **Use only the last 36 monthly returns**. The selected-input comparison should move from 70% VOO / 30% EEM to 80% VOO / 20% EEM and show a 10 percentage point sleeve move. The sidebar also controls annual cost, the EEM cap, and the VOO return haircut. The reference stress table stays anchored to the saved snapshot.

`app.py` renders the dashboard, `analysis.py` applies the mandate and stress scenarios, and `portfolio.py` contains the Lab 15 estimation and allocation engine. The included `prices.csv` holds month-end Yahoo Finance adjusted closes. The app needs no market-data credentials or network calls during analysis. The return and risk figures are historical estimates from one sample. The point-in-time signal is a timing diagnostic and does not set weights.

Run `python -X utf8 analysis.py` to reproduce the [visible output](docs/visible-output.md) as Markdown.

- [Lab 20 DRIVER checkout](docs/lab-20.md)
- [Decision memo](docs/decision-memo.md)
- [Validation and AI use](docs/validation-and-ai-use.md)
- [Signal data card](docs/data-card.md)
- [Manifest](docs/manifest.md)
