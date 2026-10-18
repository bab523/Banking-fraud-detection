import json, glob
import numpy as np, pandas as pd
import streamlit as st

st.set_page_config(page_title="Banking Fraud Detection", page_icon="🛡️", layout="wide")
pred = pd.read_parquet("dashboard_data/predictions.parquet")
m = json.load(open("dashboard_data/metrics.json"))

flagged = pred[pred.prediction == 1]
actual = pred[pred.actual_class == 1]
caught = flagged[flagged.actual_class == 1]
rule_caught = pred[(pred.rule_alert == 1) & (pred.actual_class == 1)]

st.title("🛡️ Real-Time Banking Fraud Detection Platform")
st.caption("Kafka (3 brokers) → ML scoring + rules → Parquet → Streamlit  |  Group 1, Data Engineering Capstone")

c = st.columns(5)
c[0].metric("Transactions scored", len(pred))
c[1].metric("Flagged as fraud", len(flagged))
c[2].metric("Actual frauds", len(actual))
c[3].metric("Frauds caught (ML)", len(caught))
c[4].metric("Recall on live sample", f"{100*len(caught)/max(len(actual),1):.1f}%")

t1, t2, t3, t4, t5 = st.tabs(["📊 Overview", "🔎 Live predictions", "🤖 Model performance",
                              "🏗️ Architecture", "🧪 Fault tolerance & limits"])

with t1:
    l, r = st.columns(2)
    l.subheader("Decisions")
    l.bar_chart(pred["decision"].value_counts())
    r.subheader("Fraud probability distribution")
    hist, edges = np.histogram(pred["fraud_probability"], bins=10, range=(0, 1))
    r.bar_chart(pd.DataFrame({"count": hist}, index=[f"{e:.1f}" for e in edges[:-1]]))
    st.subheader("ML model vs simple rules (same transactions)")
    st.dataframe(pd.DataFrame({
        "Method": ["Rule engine (score ≥ 2)", "ML model (Random Forest)"],
        "Frauds caught": [len(rule_caught), len(caught)],
        "Total alerts": [int(pred.rule_alert.sum()), len(flagged)],
        "Missed frauds": [len(actual) - len(rule_caught), len(actual) - len(caught)]}),
        hide_index=True, use_container_width=True)

with t2:
    choice = st.selectbox("Show", ["All", "FRAUD", "LEGITIMATE"])
    view = pred if choice == "All" else pred[pred.decision == choice]
    st.dataframe(view.sort_values("fraud_probability", ascending=False),
        hide_index=True, use_container_width=True,
        column_config={"fraud_probability": st.column_config.ProgressColumn(
            "fraud_probability", min_value=0, max_value=1, format="%.4f")})

with t3:
    st.info(f"Evaluated on a held-out test set of {m['test_rows']:,} transactions "
            f"({m['test_frauds']} frauds, real ratio ≈ 0.17%). Threshold {m['threshold']} chosen on a separate validation set.")
    k = st.columns(5)
    k[0].metric("Precision", m["precision"]); k[1].metric("Recall", m["recall"])
    k[2].metric("F1", m["f1"]); k[3].metric("ROC-AUC", m["roc_auc"]); k[4].metric("PR-AUC", m["pr_auc"])
    l, r = st.columns(2)
    l.subheader("Confusion matrix (test set)")
    l.dataframe(pd.DataFrame([[m["tn"], m["fp"]], [m["fn"], m["tp"]]],
        index=["Actual legit", "Actual fraud"], columns=["Pred legit", "Pred fraud"]))
    r.subheader("Top features")
    r.bar_chart(pd.Series(m["top_features"]))

with t4:
    st.graphviz_chart("""
    digraph G { rankdir=LR; node [shape=box, style=rounded];
      Data [label="Kaggle creditcard.csv"]; Prod [label="Python Producer\\n(acks=all)"];
      K [label="Kafka cluster\\n3 brokers, KRaft\\ntxn_live: 3 partitions, RF=3"];
      Score [label="Scoring\\nRandom Forest + rules"]; P [label="Parquet\\npredictions"]; D [label="Streamlit\\nDashboard"];
      Data -> Prod -> K -> Score -> P -> D; }""")
    st.markdown("**Stack:** Docker Compose, Apache Kafka 3.8 (KRaft), MySQL 8, Python, scikit-learn, Streamlit, GitHub.")

with t5:
    st.subheader("Fault tolerance drill")
    st.write("One broker (kafka2) was stopped; ISR shrank to 2 brokers, producer kept working, "
             "and ISR recovered to 3 after restart.")
    for p in sorted(glob.glob("docs/*.png")):
        st.image(p, caption=p.split("/")[-1])
    st.subheader("Limitations")
    st.markdown("- Laptop RAM (4.8 GB): Spark Streaming, HBase, Hive, Airflow replaced by lightweight tools.\n"
                "- Scoring runs as a micro-batch over the Kafka topic, not a continuous stream.\n"
                "- Dataset features are anonymised (PCA), so rules are not business-readable.")
