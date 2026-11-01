"""Uber hot zones in New York City: Streamlit dashboard (data computed by notebooks/uber_hot_zones.ipynb)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

HERE = Path(__file__).parent
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
METHODS = {"KMeans (10 zones)": "kmeans", "DBSCAN (dense cores)": "dbscan"}
MAP_STYLE = "carto-positron"

st.set_page_config(page_title="Uber hot zones NYC", page_icon="🚕", layout="wide")


@st.cache_data
def load():
    zones = pd.read_csv(HERE / "hotzones.csv")
    metrics = pd.read_csv(HERE / "metrics.csv")
    heat = pd.read_csv(HERE / "demand_heatmap.csv", index_col=0)
    pickups = pd.read_csv(HERE / "pickups_sample.csv.gz")
    return zones, metrics, heat, pickups


zones, metrics, heat, pickups = load()

st.title("🚕 Uber hot zones in New York City")
st.caption("Where should drivers be? Hot zones computed from 4.5 million Uber pickups (April-September 2014), "
           "for each day of week and hour, with two clustering algorithms.")

with st.sidebar:
    st.header("Slice")
    day = st.selectbox("Day of week", DAYS, index=4)
    hour = st.slider("Hour", 0, 23, 18)
    method_label = st.radio("Algorithm", list(METHODS))
    show_points = st.checkbox("Show pickups (sample)", value=True)
method = METHODS[method_label]
wd = DAYS.index(day)

z = zones[(zones["method"] == method) & (zones["weekday"] == wd) & (zones["hour"] == hour)].sort_values("rank")
m = metrics[(metrics["method"] == method) & (metrics["weekday"] == wd) & (metrics["hour"] == hour)].iloc[0]

c = st.columns(4)
c[0].metric("Avg pickups in this hour", f"{heat.loc[wd, str(hour)]:.0f}")
c[1].metric("Hot zones", int(m["n_zones"]))
c[2].metric("Pickups within 1 km of a zone", f"{m['coverage_1km']:.0%}")
c[3].metric("Pickups outside any zone (noise)", f"{m['noise_share']:.0%}")

left, right = st.columns([3, 2])
with left:
    fig = px.scatter_map(z, lat="lat", lon="lon", size="avg_pickups_per_hour", hover_name="zone",
                         hover_data={"rank": True, "avg_pickups_per_hour": ":.0f", "lat": False, "lon": False},
                         size_max=40, zoom=10.5, center=dict(lat=40.74, lon=-73.97), height=620, map_style=MAP_STYLE)
    fig.update_traces(marker=dict(color="#e4002b", opacity=0.8))
    if show_points:
        pts = pickups[(pickups["weekday"] == wd) & (pickups["hour"] == hour)]
        p = px.scatter_map(pts, lat="lat", lon="lon")
        p.update_traces(marker=dict(size=3, color="#1f4e79", opacity=0.25), hoverinfo="skip")
        fig.add_traces(p.data)
        fig.data = fig.data[::-1]  # pickups below the zone pins
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader(f"Where to be on {day} at {hour}:00")
    t = z[["rank", "zone", "avg_pickups_per_hour", "share"]].rename(columns={
        "avg_pickups_per_hour": "avg pickups / hour", "share": "share of the hour's pickups"})
    st.dataframe(t.style.format({"avg pickups / hour": "{:.0f}", "share of the hour's pickups": "{:.1%}"}),
                 hide_index=True, width="stretch", height=560)

st.header("Demand by day and hour")
fig = px.imshow(heat.values, x=list(range(24)), y=DAYS, aspect="auto", color_continuous_scale="Viridis",
                labels=dict(x="hour", y="", color="avg pickups / hour"))
st.plotly_chart(fig, width="stretch")

st.header("KMeans vs DBSCAN on the 168 slices")
summary = metrics.groupby("method").agg(avg_zones=("n_zones", "mean"), avg_noise=("noise_share", "mean"),
                                        avg_coverage_1km=("coverage_1km", "mean")).rename(index={"kmeans": "KMeans", "dbscan": "DBSCAN"})
st.dataframe(summary.style.format({"avg_zones": "{:.1f}", "avg_noise": "{:.0%}", "avg_coverage_1km": "{:.0%}"}), width="content")
mm = metrics.assign(slot=metrics["weekday"] * 24 + metrics["hour"])
fig = px.line(mm, x="slot", y="coverage_1km", color="method", hover_data=["day", "hour", "n_zones"],
              labels={"slot": "slot (0 = Monday 0h, 167 = Sunday 23h)", "coverage_1km": "pickups within 1 km of a zone"})
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(fig, width="stretch")
st.caption("Coverage = share of the slice's pickups less than 1 km (about a 4-6 minute drive in Manhattan) from a hot zone center. "
           "Zone names = nearest landmark within 1.5 km.")
