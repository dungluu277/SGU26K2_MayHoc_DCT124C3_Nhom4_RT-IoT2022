from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.demo_utils import DATA_DIR, PROJECT_SUMMARY, render_header


render_header(
    "RT-IoT2022 IoT Traffic Classification",
    "Machine Learning research dashboard · Saigon University",
)

dataset = PROJECT_SUMMARY["dataset"]
test = PROJECT_SUMMARY["selected_model"]["test"]
st.caption(
    f"Offline demonstration using the RT-IoT2022 dataset · "
    f"{dataset['raw_rows']:,} raw flows reduced to {dataset['clean_rows']:,} "
    "after the documented cleaning process."
)

with st.container(border=True):
    cards = st.columns(5)
    cards[0].metric("Clean flows", f"{dataset['clean_rows']:,}")
    cards[1].metric("Input features", f"{dataset['input_features']}")
    cards[2].metric("Traffic classes", f"{dataset['classes']}")
    cards[3].metric("Test accuracy", f"{test['accuracy']:.2%}")
    cards[4].metric("Test Macro-F1", f"{test['macro_f1']:.4f}")
st.caption(
    "Test metrics are the group's reported held-out evaluation results; "
    "they are not recalculated from uploaded prediction data."
)

st.subheader("Traffic class distribution")
try:
    class_counts = pd.read_csv(DATA_DIR / "class_distribution.csv")
except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error(f"Could not load the saved class distribution: {error}")
else:
    required = {"label", "count", "percentage"}
    if not required.issubset(class_counts.columns):
        st.error("The saved class distribution is missing required columns.")
    else:
        class_counts = class_counts.sort_values("count", ascending=True)
        chart = px.bar(
            class_counts,
            x="count",
            y="label",
            orientation="h",
            log_x=True,
            hover_data={"percentage": ":.2f", "count": ":,"},
            color_discrete_sequence=["#1E3A5F"],
            labels={"count": "Flows (log scale)", "label": "Traffic class"},
        )
        chart.update_layout(
            height=440,
            margin=dict(l=12, r=16, t=18, b=12),
            xaxis=dict(
                type="log",
                tickmode="array",
                tickvals=[10, 100, 1_000, 10_000, 100_000],
                ticktext=["10", "100", "1k", "10k", "100k"],
                gridcolor="#E2E8F0",
            ),
            yaxis=dict(title=None, automargin=True),
            showlegend=False,
        )
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
        st.caption(
            f"Majority class: {dataset['majority_class']} "
            f"({dataset['majority_count']:,} flows) · "
            f"Rarest class: {dataset['rarest_class']} "
            f"({dataset['rarest_count']:,} flows)."
        )

st.subheader("Research workflow")
workflow = [
    ("01", "Dataset", "RT-IoT2022 source flows"),
    ("02", "Preprocessing", "Cleaning and feature preparation"),
    ("03", "Experiments", "Decision Tree, Random Forest and MLP"),
    ("04", "Model selection", "Cross-validation and Validation"),
    ("05", "Final evaluation", "One held-out Test evaluation"),
    ("06", "Saved pipeline", "Preprocessing plus balanced RF"),
    ("07", "Demo inference", "Offline CSV upload and analysis"),
]
for start in (0, 4):
    steps = workflow[start : start + 4]
    columns = st.columns(len(steps))
    for column, (number, title, description) in zip(columns, steps):
        with column, st.container(border=True):
            st.caption(number)
            st.markdown(f"**{title}**")
            st.caption(description)

st.subheader("Research highlights")
highlights = st.columns(3)
with highlights[0], st.container(border=True):
    st.markdown("**Imbalanced multiclass dataset**")
    st.write(
        f"The cleaned dataset contains {dataset['classes']} labels with a "
        "substantial difference in class support."
    )
with highlights[1], st.container(border=True):
    st.markdown("**Selected model**")
    st.write(
        "The final Random Forest uses 100 trees and balanced-sub-sample class "
        "weights, with fitted preprocessing in the saved pipeline."
    )
with highlights[2], st.container(border=True):
    st.markdown("**Held-out Test**")
    st.write(
        f"The report records {test['errors']} errors across {test['rows']:,} "
        "Test flows. This result is dataset-specific, not a guarantee on "
        "new traffic."
    )

with st.expander("Additional exploratory figures from the source project"):
    assets = Path(__file__).parent.parent / "assets"
    left, right = st.columns(2)
    heatmap = assets / "spearman_heatmap.png"
    duration_plot = assets / "flow_duration_by_class.png"
    if heatmap.is_file():
        left.image(
            str(heatmap),
            caption="Spearman correlation heatmap from the source EDA.",
            width="stretch",
        )
    if duration_plot.is_file():
        right.image(
            str(duration_plot),
            caption="Flow duration distribution by class from the source EDA.",
            width="stretch",
        )

with st.expander("Model, label mapping and evaluation notes"):
    st.write(
        "The fitted sklearn pipeline applies One-Hot Encoding to proto and "
        "service and passes the 80 numeric features through. It was fit on "
        "Train and Validation after model selection."
    )
    st.write(
        "The verified benign labels are MQTT_Publish, Thing_Speak and "
        "Wipro_bulb. The other nine RT-IoT2022 labels are attack classes."
    )
    st.write(
        "The Test set includes only 5 Metasploit_Brute_Force_SSH examples "
        "and 4 NMAP_FIN_SCAN examples; per-class scores for such small "
        "supports are uncertain."
    )
    st.caption(
        "The source project did not include a serialized model artifact. "
        "This standalone demo contains the exported pipeline and did not "
        "modify the source project."
    )
