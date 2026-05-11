# Clinical Response Interpreter

Clinical Response Interpreter is a FastAPI app for interpreting free-text patient responses to clinical screening questions as `Yes`, `No`, or `Unclear`. It is built around a spaCy text classification model trained on yes/no responses to DAST-10 questions.

The app currently includes:

- A JSON API with `POST /predict` and `GET /health`
- A plain HTML/CSS/JavaScript demo at `GET /`
- A spaCy-backed predictor that can load either an installed model package or a local model directory
- A mock predictor mode for tests and local API smoke checks
- A direct Makefile-based training workflow that avoids `spacy project run`

## Project Structure

```text
clinical-response-interpreter/
├── app/
│   ├── main.py              # FastAPI app, routes, static frontend mount
│   ├── predictor.py         # spaCy/package/path/mock predictor implementations
│   ├── schemas.py           # Pydantic request/response models
│   ├── settings.py          # Environment-driven settings
│   └── static/              # Plain frontend demo
├── tests/
│   ├── test_api.py
│   └── test_predictor.py
├── training/
│   ├── assets/              # JSONL training/eval data
│   ├── configs/config.cfg   # spaCy training config
│   ├── scripts/convert.py   # JSONL to .spacy converter
│   ├── scripts/prepare_dataset_legacy.py
│   └── project.yml          # Copied spaCy project file
├── Makefile                 # Direct training workflow
├── requirements.txt
└── requirements-dev.txt
```

Generated training outputs such as `training/corpus/`, `training/output/`, and `training/packages/` are ignored by git.

## Installation

From the project root:

```bash
cd clinical-response-interpreter
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For tests:

```bash
python -m pip install -r requirements-dev.txt
```

Important: `requirements.txt` currently includes a local file reference to a generated model package under `training/packages/en_yes_no_detection-0.1.3/...`. If that artifact is not present on your machine, `pip install -r requirements.txt` will fail. In that case, either restore/build the package artifact first, or install the non-model dependencies you need for mock-mode development separately.

## Running The Server

Mock mode, which does not require spaCy model loading:

```bash
MODEL_SOURCE=mock MODEL_VERSION=mock-0.1.0 uvicorn app.main:app --reload
```

Installed package mode, the default:

```bash
MODEL_SOURCE=package MODEL_PACKAGE=en_yes_no_detection MODEL_VERSION=0.1.3 uvicorn app.main:app --reload
```

Local model path mode:

```bash
MODEL_SOURCE=path MODEL_PATH=training/output/model-best MODEL_VERSION=0.1.3 uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

The interactive demo submits requests to `POST /predict`.

## Endpoints

### `GET /`

Serves the static frontend demo from `app/static/index.html`.

### `GET /health`

Returns the active predictor configuration and load status. It does not expose secrets.

Example response:

```json
{
  "status": "ok",
  "predictor_loaded": true,
  "model_source": "mock",
  "model_package": "en_yes_no_detection",
  "model_path": null,
  "model_version": "mock-0.1.0"
}
```

### `POST /predict`

Request body:

```json
{
  "question": "Have you used drugs other than those required for medical reasons?",
  "response": "No, I have not."
}
```

Response body:

```json
{
  "predicted_answer": "No",
  "confidence": 0.88,
  "scores": {
    "YES": 0.12,
    "NO": 0.88
  },
  "needs_clarification": false,
  "model_version": "mock-0.1.0"
}
```

The response format is the same for mock and spaCy-backed predictions.

If the highest model score is below `CLARIFICATION_THRESHOLD`, the app returns:

```json
{
  "predicted_answer": "Unclear",
  "confidence": 0.52,
  "scores": {
    "YES": 0.52,
    "NO": 0.48
  },
  "needs_clarification": true,
  "model_version": "mock-0.1.0"
}
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `MODEL_SOURCE` | `package` | Predictor source. Supported values are `package`, `path`, and `mock`. |
| `MODEL_PATH` | unset | Local spaCy model directory. Required when `MODEL_SOURCE=path`. |
| `MODEL_PACKAGE` | `en_yes_no_detection` | Python package to import when `MODEL_SOURCE=package`. |
| `CLARIFICATION_THRESHOLD` | `0.70` | Minimum confidence required to return `Yes` or `No`. Below this, the result is `Unclear`. |
| `MODEL_VERSION` | `unknown` | Version string returned in API responses and health output. |

## Testing

The API tests force mock mode, so they do not require a real spaCy model.

```bash
MODEL_SOURCE=mock MODEL_VERSION=mock-0.1.0 python -m pytest
```

Current tests cover:

- `GET /health`
- `POST /predict` for yes-like and no-like responses
- validation errors for missing or empty `question` / `response`
- prediction formatting logic for `Yes`, `No`, and `Unclear`

## spaCy Training Workflow

The repository includes a copied spaCy training pipeline under `training/`. Because the spaCy project CLI behaved inconsistently in this environment, there is a Makefile that can be used if the spacy project run commands don't work.

Run commands from the project root:

```bash
make convert
make train
make evaluate
make package
```

Or run everything:

```bash
make all
```

The Makefile runs:

```bash
python training/scripts/convert.py en training/assets/yes_no_training.jsonl training/corpus/train.spacy
python training/scripts/convert.py en training/assets/yes_no_eval.jsonl training/corpus/dev.spacy
python -m spacy train training/configs/config.cfg --output training/output/ --paths.train training/corpus/train.spacy --paths.dev training/corpus/dev.spacy --nlp.lang en --gpu-id 0
python -m spacy evaluate training/output/model-best training/corpus/dev.spacy --output training/output/metrics.json
python -m spacy package training/output/model-best training/packages --name yes_no_detection --version 0.1.4 --force
```

The copied `training/project.yml` is still present, but the Makefile is the documented workflow for this project right now.

You can also use the following spacy commands which reference the project.yml file to achieve the same result:

```bash
python -m spacy project run convert
python -m spacy project run train
python -m spacy project run evaluate
python -m spacy project run package
```

Or run everything:

```bash
python -m spacy project run all
```

## Data Format

Training and evaluation data are JSONL files:

- `training/assets/yes_no_training.jsonl`
- `training/assets/yes_no_eval.jsonl`

Each line is a JSON object with:

```json
{
  "text": "Have you used drugs other than those required for medical reasons? No, I have not.",
  "cats": {
    "YES": 0,
    "NO": 1
  }
}
```

`training/scripts/convert.py` converts these JSONL files into spaCy `DocBin` files under `training/corpus/`.

## Limitations

- The model predicts only among `YES` and `NO`; ambiguity is handled by thresholding the confidence score.
- The app does not currently return explanations or highlighted evidence.
- The default `MODEL_SOURCE=package` requires an installed `en_yes_no_detection` package.
- `MODEL_VERSION` is supplied by environment variable; it is not automatically read from spaCy model metadata.
- `training/scripts/prepare_dataset_legacy.py` is copied legacy code and has not been refactored.
- No Dockerfile is currently implemented in this project.

## Future Improvements

- Refactor the legacy dataset preparation script into a safe, repeatable CLI.
- Add a small config file or `.env.example` for common runtime settings.
- Add Docker support for serving and training.
- Add model metadata loading so `model_version` can come from the installed spaCy model.
- Add tests for package/path model loading with a tiny fixture model.
- Add richer frontend error handling and display health/model status in the demo.
- Add calibration and validation reports for the `CLARIFICATION_THRESHOLD`.
