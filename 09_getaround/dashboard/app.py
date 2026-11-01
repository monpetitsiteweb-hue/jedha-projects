"""Getaround - late checkout analysis dashboard (Streamlit)."""
import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import SCOPES, load_raw, prepare, simulate, simulation_grid

st.set_page_config(page_title="Getaround - Delay analysis", page_icon="🚗", layout="wide")
COLORS = {"mobile": "#1f77b4", "connect": "#e377c2", "All cars": "#1f77b4", "Connect only": "#e377c2"}


@st.cache_data
def get_data():
    df = prepare(load_raw())
    return df, simulation_grid(df)


df, grid = get_data()
ended = df[df["state"] == "ended"]
pairs = df[df["has_previous"]]

st.title("🚗 Getaround: minimum delay between two rentals")
st.caption("Data: 2017 rentals (rentals_data). Helps the Product team choose the **threshold** and **scope** of the feature.")

# ---------------------------------------------------------------- overview
st.header("1. Overview")
c = st.columns(5)
c[0].metric("Rentals", f"{len(df):,}")
c[1].metric("Canceled", f"{(df.state == 'canceled').mean():.1%}")
c[2].metric("Connect share", f"{(df.checkin_type == 'connect').mean():.1%}")
c[3].metric("Late at checkout (ended, known delay)", f"{ended.dropna(subset=['delay_at_checkout_in_minutes'])['is_late'].mean():.1%}")
c[4].metric("Rentals with a previous rental < 12h", f"{len(pairs):,} ({len(pairs) / len(df):.1%})")

col1, col2 = st.columns(2)
with col1:
    d = ended.dropna(subset=["delay_at_checkout_in_minutes"])
    clip = d["delay_at_checkout_in_minutes"].clip(-240, 480)
    fig = px.histogram(d.assign(delay=clip), x="delay", color="checkin_type", color_discrete_map=COLORS, nbins=72, barmode="overlay",
                       title="Delay at checkout (minutes, clipped to [-240, 480])", labels={"delay": "minutes"})
    st.plotly_chart(fig, width="stretch")
with col2:
    late = d.assign(bucket=pd.cut(d["delay_at_checkout_in_minutes"], [-1e9, 0, 15, 30, 60, 120, 240, 1e9],
                                  labels=["on time / early", "1-15", "15-30", "30-60", "1-2h", "2-4h", "> 4h"]))
    share = late.groupby(["checkin_type", "bucket"], observed=False).size().groupby(level=0).transform(lambda s: s / s.sum()).reset_index(name="share")
    fig = px.bar(share, x="bucket", y="share", color="checkin_type", color_discrete_map=COLORS, barmode="group", title="Checkout delay by flow",
                 labels={"bucket": "delay (minutes)"})
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- impact on next driver
st.header("2. How often are drivers late for the next check-in, and what does it cause?")
prob = pairs[pairs["is_problematic"]]
c = st.columns(4)
c[0].metric("Consecutive rentals (gap < 12h)", f"{len(pairs):,}")
c[1].metric("Problematic cases (next driver waits)", f"{len(prob):,} ({len(prob) / len(pairs):.1%})")
c[2].metric("Median wait of the next driver", f"{prob['waiting_minutes'].median():.0f} min" if len(prob) else "n/a")
canc_prob = prob["state"].eq("canceled").mean()
canc_ok = pairs.loc[~pairs["is_problematic"] & pairs["previous_delay"].notna(), "state"].eq("canceled").mean()
c[3].metric("Cancellation rate of the next rental", f"{canc_prob:.1%}", f"{canc_prob - canc_ok:+.1%} vs non-problematic", delta_color="inverse")
st.caption("A case is problematic when the previous driver's checkout delay is longer than the planned gap between the two rentals. "
           "Rentals with an unknown previous delay stay in the denominator of the share of problematic cases, and are excluded from the cancellation comparison.")
fig = px.histogram(pairs, x="time_delta_with_previous_rental_in_minutes", color="checkin_type", color_discrete_map=COLORS, nbins=48, barmode="overlay",
                   title="Planned gap between two consecutive rentals (minutes)")
st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- simulator
st.header("3. Simulator: threshold and scope")
left, right = st.columns([1, 3])
with left:
    threshold = st.slider("Minimum delay (minutes)", 0, 720, 120, 15)
    scope = st.radio("Scope", list(SCOPES))
r = simulate(df, threshold, scope)
with right:
    c = st.columns(3)
    c[0].metric("Rentals affected (blocked)", f"{r['affected_rentals']:,}", f"{r['affected_share_all_rentals']:.2%} of all rentals", delta_color="off")
    c[1].metric("Revenue potentially affected (proxy)", f"{r['affected_share_ended_rentals']:.2%}",
                "share of ended rentals that could not be booked", delta_color="off")
    c[2].metric("Problematic cases solved", f"{r['solved_cases']} / {r['problematic_cases_in_scope']}",
                f"{r['solved_share']:.0%}" if r['problematic_cases_in_scope'] else "n/a", delta_color="off")
st.caption("The dataset has no price per rental: the share of owners' revenue affected is estimated with the share of **ended** rentals "
           "that would have been blocked, assuming an equal average revenue per rental.")

g = grid.copy()
col1, col2 = st.columns(2)
with col1:
    fig = px.line(g, x="threshold", y="affected_share_ended_rentals", color="scope", color_discrete_map=COLORS, markers=True,
                  title="Revenue potentially affected vs threshold", labels={"affected_share_ended_rentals": "share of ended rentals"})
    fig.add_vline(x=threshold, line_dash="dash"); fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig, width="stretch")
with col2:
    fig = px.line(g, x="threshold", y="solved_share", color="scope", color_discrete_map=COLORS, markers=True,
                  title="Share of problematic cases solved vs threshold (each scope over its own cases)", labels={"solved_share": "solved"})
    fig.add_vline(x=threshold, line_dash="dash"); fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

g["solved_per_100_blocked"] = 100 * g["solved_cases"] / g["affected_rentals"].replace(0, pd.NA)
fig = px.line(g, x="threshold", y="solved_per_100_blocked", color="scope", color_discrete_map=COLORS, markers=True,
              title="Efficiency: problematic cases solved per 100 rentals blocked")
st.plotly_chart(fig, width="stretch")

with st.expander("Simulation table"):
    st.dataframe(g, width="stretch")

st.header("4. Takeaways for the Product team")
st.markdown("""
- **Recommendation: all cars, 120 minutes.** This solves 67% of the problematic cases and exposes 3.3% of revenue. The 3.3% is a maximum, because a blocked rental is not necessarily lost.
- The marginal benefit drops beyond 120 minutes: 120 to 240 min solves only ~14 percentage points more while blocking ~50% more rentals.
- **Connect only, for comparison:** about two thirds of the problematic cases come from the mobile flow (149 of 218). At 120 min, Connect only exposes 1.4% of revenue but solves 49 cases, against 147 for all cars.
""")

st.header("5. Methodology")
st.markdown("""
- **Affected rental**: a rental in scope whose planned gap with the previous rental of the same car is shorter than the threshold. It could not be booked with these times.
- **Problematic case**: the previous driver's checkout delay is longer than the planned gap, so the next driver waits.
- **Solved case**: a problematic case whose gap is below the threshold and whose previous delay is at most the threshold (a gap of `threshold` minutes would have absorbed the delay).
- Gaps are only known when the previous rental ended less than 12 hours before (dataset limitation).
""")
