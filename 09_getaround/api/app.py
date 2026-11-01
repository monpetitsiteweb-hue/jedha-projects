"""Getaround pricing API: FastAPI app serving the rental price model at POST /predict."""
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

HERE = Path(__file__).parent
MODEL = joblib.load(HERE / "model.joblib")
META = json.loads((HERE / "model_meta.json").read_text(encoding="utf-8"))
FEATURES: List[str] = META["features"]
BOOL, NUM = META["boolean"], META["numeric"]

EXAMPLE_ROW = ["Citroën", 140411, 100, "diesel", "black", "convertible", True, True, False, False, True, True, True]

app = FastAPI(
    title="Getaround Pricing API",
    description="Predicts the optimal rental price per day of a car. Full documentation at /docs.",
    version="1.0.0",
    docs_url="/swagger",  # interactive Swagger UI; /docs is the custom documentation page below
    redoc_url=None,
)


class PredictInput(BaseModel):
    input: List[Union[List[Union[bool, int, float, str]], Dict[str, Any]]] = Field(
        ..., examples=[[EXAMPLE_ROW]],
        description=f"List of cars. Each car is a list of {len(FEATURES)} values in this order: {', '.join(FEATURES)}. "
                    "A dict {feature: value} per car is also accepted.",
    )


class PredictOutput(BaseModel):
    prediction: List[float]


def to_bool(v: Any) -> int:
    if isinstance(v, str):
        if v.strip().lower() in ("true", "1", "yes"):
            return 1
        if v.strip().lower() in ("false", "0", "no"):
            return 0
        raise ValueError(f"cannot read {v!r} as a boolean")
    return int(bool(v))


def to_frame(rows: list) -> pd.DataFrame:
    records = []
    for i, row in enumerate(rows):
        if isinstance(row, dict):
            missing = [f for f in FEATURES if f not in row]
            if missing:
                raise HTTPException(422, f"row {i}: missing features {missing}")
            records.append([row[f] for f in FEATURES])
        else:
            if len(row) != len(FEATURES):
                raise HTTPException(422, f"row {i}: expected {len(FEATURES)} values ({', '.join(FEATURES)}), got {len(row)}")
            records.append(list(row))
    df = pd.DataFrame(records, columns=FEATURES)
    try:
        for c in BOOL:
            df[c] = df[c].map(to_bool)
        for c in NUM:
            df[c] = pd.to_numeric(df[c])
    except (ValueError, TypeError) as e:
        raise HTTPException(422, f"invalid value: {e}")
    return df


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.get("/health")
def health():
    """Liveness check."""
    return {"status": "ok"}


@app.get("/features")
def features():
    """Expected feature order, known categories and model test performance."""
    return META


@app.post("/predict", response_model=PredictOutput)
def predict(payload: PredictInput):
    """Predict the rental price per day (EUR) for each car of `input`."""
    if not payload.input:
        raise HTTPException(422, "input must contain at least one car")
    preds = MODEL.predict(to_frame(payload.input))
    return {"prediction": [round(float(p), 2) for p in preds]}


DOCS_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Getaround Pricing API - Documentation</title>
<style>
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:0 auto;padding:24px 16px;color:#1d1d1f;line-height:1.55;background:#fff}
 h1{color:#b01aa7;margin-bottom:4px} h2{border-bottom:2px solid #eee;padding-bottom:4px;margin-top:36px}
 code,pre{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px} pre{background:#f5f5f7;padding:14px;border-radius:8px;overflow-x:auto}
 table{border-collapse:collapse;width:100%;font-size:14px} td,th{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top} th{background:#fafafa}
 .m{display:inline-block;padding:2px 8px;border-radius:4px;color:#fff;font-weight:600;font-size:13px}.post{background:#49cc90}.get{background:#61affe}
</style></head><body>
<h1>Getaround Pricing API</h1>
<p>Machine Learning API that suggests the optimal <b>rental price per day (EUR)</b> of a car on Getaround, based on its characteristics.
Model: gradient boosting (scikit-learn) trained on 4,841 cars. Test performance: R&sup2; = __R2__, mean absolute error = __MAE__ EUR.</p>
<p>Interactive documentation (try the endpoints in the browser): <a href="/swagger">/swagger</a></p>

<h2><span class="m post">POST</span> /predict</h2>
<p>Returns the predicted price per day for one or several cars.</p>
<h3>Input (JSON body)</h3>
<p>Key <code>input</code>: a list of cars. Each car is a list of <b>13 values, in this exact order</b>:</p>
<table><tr><th>#</th><th>Feature</th><th>Type</th><th>Values</th></tr>__ROWS__</table>
<pre>{
  "input": [
    ["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true],
    ["Peugeot", 72000, 110, "petrol", "grey", "estate", false, true, true, false, true, false, false]
  ]
}</pre>
<p>Each car can also be sent as an object <code>{"model_key": "Citroën", "mileage": 140411, ...}</code>. Unknown categories are accepted (treated as "other").</p>
<h3>Output</h3>
<p>JSON with one key <code>prediction</code>: list of predicted prices (EUR per day), in the same order as the input.</p>
<pre>{"prediction": [107.82, 133.88]}</pre>
<h3>Errors (bonus)</h3>
<p>HTTP 422 with a <code>detail</code> message if a car does not have 13 values, a numeric value is not a number, or a boolean cannot be read.</p>
<h3>Examples</h3>
<pre>curl -i -H "Content-Type: application/json" -X POST \\
  -d '{"input": [["Citroën", 140411, 100, "diesel", "black", "convertible", true, true, false, false, true, true, true]]}' \\
  __BASE__/predict</pre>
<pre>import requests

response = requests.post("__BASE__/predict", json={
    "input": [["Citroën", 140411, 100, "diesel", "black", "convertible", True, True, False, False, True, True, True]]
})
print(response.json())</pre>

<h2><span class="m get">GET</span> /features</h2>
<p>No input. Returns the expected feature order, the categories seen during training and the model test metrics.</p>
<h2><span class="m get">GET</span> /health</h2>
<p>No input. Returns <code>{"status": "ok"}</code> when the API is up.</p>
<h2><span class="m get">GET</span> /docs</h2>
<p>No input. Returns this page.</p>
<h2><span class="m get">GET</span> /swagger</h2>
<p>No input. Opens the interactive documentation, to try the endpoints in the browser.</p>
<h2><span class="m get">GET</span> /openapi.json</h2>
<p>No input. Returns the machine-readable description of the API (OpenAPI schema).</p>
</body></html>"""


def feature_rows() -> str:
    cats = META["categories"]
    out = []
    for i, f in enumerate(FEATURES, 1):
        if f in cats:
            t, v = "string", ", ".join(cats[f])
        elif f in BOOL:
            t, v = "boolean", "true / false"
        else:
            t, v = "number", {"mileage": "kilometers", "engine_power": "horsepower"}.get(f, "")
        out.append(f"<tr><td>{i}</td><td><code>{f}</code></td><td>{t}</td><td>{v}</td></tr>")
    return "".join(out)


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def docs(request: Request):
    base = str(request.base_url).rstrip("/")
    if request.headers.get("x-forwarded-proto") == "https":  # behind the Hugging Face proxy
        base = base.replace("http://", "https://", 1)
    return (DOCS_HTML.replace("__ROWS__", feature_rows()).replace("__BASE__", base)
            .replace("__R2__", f"{META['test_r2']:.2f}").replace("__MAE__", f"{META['test_mae']:.1f}"))
