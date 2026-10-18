import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fraud Dashboard", layout="wide")
st.title("Real-Time Banking Fraud Detection")

df = pd.read_parquet("data/output/scored.parquet")
alerts = df[df["is_alert"] == 1]
frauds = df[df["Class"] == 1]
caught = alerts[alerts["Class"] == 1]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total transactions", len(df))
c2.metric("Alerts raised", len(alerts))
c3.metric("Actual frauds", len(frauds))
c4.metric("Frauds caught", len(caught))
c5.metric("Detection rate", f"{100*len(caught)/max(len(frauds),1):.1f}%")

l, r = st.columns(2)
l.subheader("Alerts by risk score")
l.bar_chart(alerts["risk_score"].value_counts().sort_index())
r.subheader("Rules fired (alerts)")
rule_cols = [c for c in df.columns if c.startswith("rule_")]
r.bar_chart(alerts[rule_cols].sum())

st.subheader("Top risky transactions")
st.dataframe(alerts.sort_values("risk_score", ascending=False).head(50))
