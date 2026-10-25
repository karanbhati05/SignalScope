# SignalScope

Social sentiment, theme detection, entity extraction, clustering, SQL and hypothesis testing.

## Run

Python 3.10+ is required. From this folder:

```console
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Open `results/report.html` in a browser. The included report and metrics were generated from the deterministic sample generator. Other generated files are created when you run the pipeline. No account, API key or network connection is needed after dependencies are installed.

## Business question

Which audience complaints and segments deserve attention, and does a randomized campaign change conversion?

## What to review

Inspect the unseen sentiment challenge failures, segment profiles and randomized experiment confidence interval.

`main.py` contains reusable functions and the command-line pipeline. `common.py` creates a portable HTML report and JSON metrics. Generated CSV, SQLite or audio artifacts make the pipeline inspectable.

## Data and limitations

Replace generated posts with consented platform exports. Keep human labels separate from production predictions. Replace the gazetteer and lexicon with evaluated learned models as data grows. The nine repeated templates are demonstration data and cannot support generalization claims.

All sample data is generated locally. No real user data, scraped content or pretrained model weights are included. Report results as simulated experiments. Avoid presenting benchmark scores as production performance.

## Deployment plan

Run the command in a scheduled batch job, archive dated outputs, and serve the static report behind your organization's access controls. Validate input schemas, alert on missing/stale inputs and track evaluation metrics by model version before production. This repository demonstrates the core pipeline; it does not include a managed deployment or monitoring service.

## Interview discussion

Explain the business objective, baseline choice, evaluation split, failure cases and next experiment. Use the generated report to show actual results, including where a baseline fails.

## Reproduce the checks

```console
python -m unittest discover -s tests -v
```

Results in `results/` are generated from deterministic simulated data. Metrics should be interpreted as demonstration results, not production claims. The code, report and metrics are committed together so reviewers can inspect the evaluation before running the pipeline. Generated CSV, SQLite and WAV files are ignored by Git.
