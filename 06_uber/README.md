# Uber Pickups: hot zones in New York City (Jedha, Unsupervised Machine Learning project)

Riders cancel when they wait more than 5-7 minutes, yet drivers are often in the wrong neighbourhood. This project finds the **hot zones** where drivers should be in New York City, for every **day of week and hour**, from 4.5 million Uber pickups (April to September 2014).

A summary in French is in `SYNTHESE.md`.

## Deliverables

| Deliverable | Where |
|---|---|
| Analysis notebook (EDA, KMeans, DBSCAN, HDBSCAN bonus, comparison, maps) | `notebooks/uber_hot_zones.ipynb` (HTML export: `notebooks/uber_hot_zones.html`) |
| Interactive maps: hot zones per day of week and hour (slider) | `maps/hotzones_kmeans_by_day_hour.html`, `maps/hotzones_dbscan_by_day_hour.html` |
| Map of the hot zones of each day of week | `maps/hotzones_by_day.html` |
| Dashboard (Streamlit): pick a day, an hour and an algorithm | `dashboard/` |

## Method

1. Coordinates projected to kilometres around NYC so that distances (KMeans inertia, DBSCAN `eps`) are real distances.
2. **Start small**: Monday 17:00-18:00. KMeans with k chosen by elbow + silhouette + business constraint (k = 10 neighbourhood-sized zones); DBSCAN with `eps` = 200 m and `min_samples` = 0.5% of the sample (50 points for a sample of 10,000); HDBSCAN as a bonus.
3. **Grow big**: both algorithms on the 168 slices (7 days x 24 hours), at most 10,000 sampled pickups per slice.
4. Comparison with silhouette and Davies-Bouldin (Monday 17:00-18:00 only), then share of noise and a business metric on the 168 slices: **share of pickups within 1 km of a hot zone center** (about a 4-6 minute drive in Manhattan), including a fair test where KMeans uses the same number of zones as DBSCAN.
5. Zones named after the nearest NYC landmark (within 1.5 km) to describe hot zones per day of week.

## Run locally

```bash
pip install pandas numpy scikit-learn plotly jupyter streamlit
jupyter notebook notebooks/uber_hot_zones.ipynb   # reads ../data/uber-trip-data/uber-raw-data-*14.csv
cd dashboard && streamlit run app.py
```

Data (not in this repository): download https://full-stack-bigdata-datasets.s3.eu-west-3.amazonaws.com/Machine+Learning+non+Supervis%C3%A9/Projects/uber-trip-data.zip and unzip it into `data/uber-trip-data/` (only the 6 files `uber-raw-data-<month>14.csv` are used).
