"""Shared logic for the Getaround delay analysis (used by the Streamlit dashboard)."""
import numpy as np
import pandas as pd

DATA_URL = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx"
SCOPES = {"All cars": ["mobile", "connect"], "Connect only": ["connect"]}


def load_raw(path: str = "get_around_delay_analysis.xlsx") -> pd.DataFrame:
    try:
        return pd.read_excel(path, sheet_name="rentals_data")
    except FileNotFoundError:
        return pd.read_excel(DATA_URL, sheet_name="rentals_data")


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    """One row per rental, enriched with the delay of the previous rental of the same car."""
    df = raw.copy()
    df["is_late"] = df["delay_at_checkout_in_minutes"] > 0
    prev = df[["rental_id", "delay_at_checkout_in_minutes", "checkin_type"]].rename(columns={
        "rental_id": "previous_ended_rental_id",
        "delay_at_checkout_in_minutes": "previous_delay",
        "checkin_type": "previous_checkin_type",
    })
    df = df.merge(prev, on="previous_ended_rental_id", how="left")
    df["has_previous"] = df["time_delta_with_previous_rental_in_minutes"].notna()
    # problematic case: previous driver returned the car later than the planned gap -> next driver waits
    df["is_problematic"] = df["has_previous"] & (df["previous_delay"] > df["time_delta_with_previous_rental_in_minutes"])
    df["waiting_minutes"] = (df["previous_delay"] - df["time_delta_with_previous_rental_in_minutes"]).clip(lower=0)
    return df


def simulate(df: pd.DataFrame, threshold: int, scope: str) -> dict:
    """Impact of a minimum delay `threshold` (minutes) applied to `scope`.

    - affected rentals: consecutive rentals in scope booked with a gap < threshold (they could not be booked as-is)
    - solved cases: problematic cases in scope with gap < threshold and a previous delay <= threshold
      (with a gap of at least `threshold`, the previous delay would have been absorbed)
    """
    in_scope = df["checkin_type"].isin(SCOPES[scope])
    gap = df["time_delta_with_previous_rental_in_minutes"]
    affected = in_scope & df["has_previous"] & (gap < threshold)
    solved = affected & df["is_problematic"] & (df["previous_delay"] <= threshold)
    n_problematic = int((df["is_problematic"] & in_scope).sum())
    return {
        "threshold": threshold,
        "scope": scope,
        "affected_rentals": int(affected.sum()),
        "affected_share_all_rentals": affected.sum() / len(df),
        "affected_ended_rentals": int((affected & (df["state"] == "ended")).sum()),
        "affected_share_ended_rentals": (affected & (df["state"] == "ended")).sum() / (df["state"] == "ended").sum(),
        "problematic_cases_in_scope": n_problematic,
        "solved_cases": int(solved.sum()),
        "solved_share": solved.sum() / n_problematic if n_problematic else np.nan,
    }


def simulation_grid(df: pd.DataFrame, thresholds=range(0, 721, 15)) -> pd.DataFrame:
    return pd.DataFrame([simulate(df, t, s) for s in SCOPES for t in thresholds])
