---
title: Getaround Pricing API
emoji: 🚗
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# Getaround Pricing API

FastAPI service predicting the rental price per day of a car.

- `POST /predict`: `{"input": [[13 values per car]]}` returns `{"prediction": [...]}`
- `GET /docs`: documentation page
- `GET /swagger`: interactive Swagger UI
- `GET /features`, `GET /health`

Run locally:

```bash
pip install -r requirements.txt
uvicorn app:app --port 7860
```
