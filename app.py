import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Oman Gold Tracker", layout="wide")
st.title("📈 Oman Gold Rate Trend")

CSV_FILE = "rates.csv"

if not os.path.exists(CSV_FILE):
    st.info("No data recorded yet. The daily cloud task will populate this automatically.")
else:
    df = pd.read_csv(CSV_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    latest = df.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("22K Gold Rate", f"{latest['rate_22k']} OMR")
    c2.metric("24K Gold Rate", f"{latest['rate_24k']} OMR")
    c3.metric("18K Gold Rate", f"{latest['rate_18k']} OMR")

    st.divider()

    time_filter = st.radio(
        "Select Range:",
        ["1 Week", "1 Month", "1 Year", "5 Years", "All Time"],
        horizontal=True,
        index=4
    )

    now = pd.Timestamp.now()
    if time_filter == "1 Week":
        filtered_df = df[df["date"] >= (now - pd.Timedelta(days=7))]
    elif time_filter == "1 Month":
        filtered_df = df[df["date"] >= (now - pd.Timedelta(days=30))]
    elif time_filter == "1 Year":
        filtered_df = df[df["date"] >= (now - pd.Timedelta(days=365))]
    elif time_filter == "5 Years":
        filtered_df = df[df["date"] >= (now - pd.Timedelta(days=365 * 5))]
    else:
        filtered_df = df

    fig = px.line(
        filtered_df,
        x="date",
        y=["rate_22k", "rate_24k", "rate_18k"],
        labels={"value": "OMR / Gram", "date": "Date", "variable": "Purity"},
        markers=True
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)