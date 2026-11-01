# Getaround Analysis (Jedha, Deployment project)

Getaround is the "Airbnb for cars". This project helps the Product team decide on a **minimum delay between two rentals** (threshold and scope) and gives the Data Science team a **pricing API** that predicts the rental price per day of a car.

## Online links

| Deliverable | URL |
|---|---|
| Dashboard (Streamlit) | https://mpsw-getaround-dashboard.hf.space |
| API documentation | https://mpsw-getaround-api.hf.space/docs |
| API endpoint | `POST https://mpsw-getaround-api.hf.space/predict` |
| Code | https://github.com/monpetitsiteweb-hue/jedha-projects/tree/main/09_getaround |

## Repository structure

```
data/                     the two data files and SOURCE.md
notebooks/
  01_delay_analysis.ipynb   late checkout analysis and threshold/scope simulation
  02_pricing_ml.ipynb       pricing model: EDA, model comparison (MLflow), tuning, export
dashboard/                Streamlit app (Hugging Face Space, Docker)
api/                      FastAPI app + trained model (Hugging Face Space, Docker)
scripts/test_api.py       calls the online /predict endpoint
docs/mlflow_compare.png   screenshot of the MLflow comparison
```

## Data

The two official files are in `data/`, and the dashboard keeps its own copy of the delay file, `dashboard/get_around_delay_analysis.xlsx`.

## Key results

**Delay analysis (2017 data, 21,310 rentals)**
- 57% of ended rentals with a known checkout are returned late (median lateness 53 min). Connect: 43%, mobile: 61%.
- 1,841 rentals follow another rental of the same car by less than 12h; 218 of them (12%) are problematic: the previous driver returns the car after the next check-in (median wait 26 min). The next rental is then canceled 17% of the time, against 11% otherwise.
- **Recommendation: all cars, 120 minutes.** This solves 67% of the problematic cases and exposes 3.3% of revenue. The 3.3% is a maximum, estimated from the share of ended rentals, because a blocked rental is not necessarily lost.
- For comparison, Connect only exposes 1.4% of revenue at 120 minutes, but solves 49 cases against 147 for all cars, because about two thirds of the problematic cases come from the mobile flow.

**Pricing model**
- Histogram gradient boosting (scikit-learn), tuned with 5-fold cross-validation.
- Test set: R² = 0.757, MAE = 10.5 EUR/day (mean-price baseline MAE: 23.6 EUR/day, average price 121 EUR/day).

## API

`POST /predict` with a list of cars, each one as 13 values in this order:
`model_key, mileage, engine_power, fuel, paint_color, car_type, private_parking_available, has_gps, has_air_conditioning, automatic_car, has_getaround_connect, has_speed_regulator, winter_tires`

The 11-value example of the brief is refused with a 422: it does not match these 13 features.

```bash
curl -i -H "Content-Type: application/json" -X POST \
  -d '{"input": [["Peugeot", 72000, 110, "petrol", "grey", "estate", false, true, true, false, true, false, false]]}' \
  https://mpsw-getaround-api.hf.space/predict
```

```python
import requests
response = requests.post("https://mpsw-getaround-api.hf.space/predict", json={
    "input": [["Citroën", 140411, 100, "diesel", "black", "convertible", True, True, False, False, True, True, True]]
})
print(response.json())  # {"prediction": [107.82]}
```

Other endpoints: `GET /docs` (documentation), `GET /swagger` (interactive), `GET /openapi.json` (machine-readable schema), `GET /features`, `GET /health`.

## Run locally

```bash
git clone https://github.com/monpetitsiteweb-hue/jedha-projects.git
cd jedha-projects/09_getaround

# dashboard -> http://localhost:8501
pip install -r dashboard/requirements.txt
cd dashboard && streamlit run app.py
cd ..

# API -> http://localhost:7860/docs
pip install -r api/requirements.txt
cd api && uvicorn app:app --port 7860
cd ..

# notebooks (run from the notebooks/ folder; 02 retrains and exports api/model.joblib)
pip install jupyter scikit-learn mlflow matplotlib openpyxl
jupyter notebook notebooks/
```

`notebooks/mlflow.db` is the local MLflow database with the 5 runs. Running `notebooks/02_pricing_ml.ipynb` writes to it.

## Deployment (Hugging Face Spaces, Docker)

```bash
pip install -U huggingface_hub
hf auth login
hf repos create MPSW/getaround-api --type space --sdk docker --exist-ok
hf upload MPSW/getaround-api api . --type space --exclude "__pycache__/*"
hf repos create MPSW/getaround-dashboard --type space --sdk docker --exist-ok
hf upload MPSW/getaround-dashboard dashboard . --type space --exclude "__pycache__/*"
```
