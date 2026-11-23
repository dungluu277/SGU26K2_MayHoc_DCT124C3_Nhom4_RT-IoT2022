from pathlib import Path

import plotly.express as px
import streamlit as st

from src.demo_utils import PROJECT_SUMMARY, load_local_csv, render_header


render_header(
    "Model Comparison",
    "Review the saved model-selection experiments and held-out Test results.",
)

try:
    experiments = load_local_csv("experiment_results.csv")
    test_results = load_local_csv("test_model_results.csv")
except FileNotFoundError as error:
    st.error(f"Saved experiment comparison data is missing: {error}")
    st.stop()

model_names = {
    "E01": "Decision Tree",
    "E05": "Random Forest",
    "E10": "MLP",
    "E06": "Random Forest Balanced",
}
test_results = test_results.copy()
test_results["Comparison model"] = test_results["Experiment"].map(model_names)
test_results["Comparison model"] = test_results["Comparison model"].fillna(
    test_results["Model"]
)
test_results = test_results.sort_values(
    "Experiment", key=lambda values: values.map({"E01": 0, "E05": 1, "E10": 2, "E06": 3})
)

test_tab, research_tab = st.tabs(
    ["Held-out Test", "Cross-validation and Validation"]
)

with test_tab:
    st.caption(
        "All four models below use saved results from the same held-out Test "
        "split. The values are reported experiment outputs, not recomputed here."
    )
    cards = st.columns(4)
    selected_test = test_results.loc[test_results["Experiment"] == "E06"].iloc[0]
    cards[0].metric("Selected model", "Random Forest Balanced")
    cards[1].metric("Test accuracy", f"{selected_test['Test Accuracy']:.4f}")
    cards[2].metric("Test Macro-F1", f"{selected_test['Test Macro-F1']:.4f}")
    cards[3].metric("Test errors", f"{int(selected_test['Errors']):,}")

    st.subheader("Comparison across held-out Test")
    charts = [
        ("Test Accuracy", "Accuracy", [0, 1.05]),
        ("Test Macro-F1", "Macro-F1", [0, 1.05]),
        ("Test Macro-Recall", "Macro-Recall", [0, 1.05]),
        ("Errors", "Misclassified flows", None),
    ]
    for start in (0, 2):
        columns = st.columns(2)
        for column, (metric, title, score_range) in zip(
            columns, charts[start : start + 2]
        ):
            figure = px.bar(
                test_results,
                x="Comparison model",
                y=metric,
                text=(
                    test_results[metric].map(lambda value: f"{value:.4f}")
                    if metric != "Errors"
                    else test_results[metric].astype(int).astype(str)
                ),
                hover_data={"Experiment": True, metric: ":.6f" if metric != "Errors" else True},
                color_discrete_sequence=["#1E3A5F"],
                labels={metric: title, "Comparison model": ""},
            )
            figure.update_traces(textposition="outside", cliponaxis=False)
            figure.update_layout(
                height=330,
                margin=dict(l=8, r=8, t=18, b=8),
                xaxis=dict(title=None, tickangle=-12),
                yaxis=dict(
                    title=title,
                    range=score_range,
                    gridcolor="#E2E8F0",
                ),
                showlegend=False,
            )
            column.plotly_chart(
                figure, width="stretch", config={"displayModeBar": False}
            )

    display_columns = [
        "Experiment",
        "Comparison model",
        "Test Accuracy",
        "Test Macro-F1",
        "Test Macro-Recall",
        "Test Macro-Precision",
        "Errors",
    ]
    st.dataframe(
        test_results.loc[:, display_columns].rename(
            columns={"Comparison model": "Model"}
        ),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Model configurations")
    detail_specs = [
        ("E01", "Decision Tree"),
        ("E05", "Random Forest"),
        ("E10", "MLP"),
        ("E06", "Random Forest Balanced"),
    ]
    detail_tabs = st.tabs([name for _, name in detail_specs])
    for detail_tab, (experiment_id, name) in zip(detail_tabs, detail_specs):
        with detail_tab:
            row = experiments.loc[experiments["Experiment"] == experiment_id].iloc[0]
            st.markdown(f"**{experiment_id} · {name}**")
            st.write(row["Configuration"])
            st.caption(
                "Test metrics are from the saved final evaluation table; "
                "cross-validation and Validation metrics are shown separately."
            )

with research_tab:
    st.caption(
        "Cross-validation and Validation were used during model selection. "
        "They are separate from the held-out Test results in the other tab."
    )
    metric = st.selectbox(
        "Selection metric",
        options=["CV Macro-F1", "Validation Macro-F1", "Validation Macro-Recall"],
    )
    family_colors = {
        "Decision Tree": "#1E3A5F",
        "Random Forest": "#2563EB",
        "MLP": "#60A5FA",
    }
    chart = px.bar(
        experiments.sort_values(metric, ascending=False),
        x="Experiment",
        y=metric,
        color="Family",
        hover_data=["Model", "CV Macro-F1 SD"],
        range_y=[0, 1.05],
        color_discrete_map=family_colors,
        labels={metric: metric},
    )
    chart.update_layout(
        height=390,
        margin=dict(l=8, r=8, t=18, b=8),
        xaxis=dict(title=None),
        yaxis=dict(gridcolor="#E2E8F0"),
        legend_title_text="Model family",
    )
    st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})

    cv_validation = experiments.loc[
        experiments["Experiment"].isin(model_names),
        [
            "Experiment",
            "Family",
            "Model",
            "CV Macro-F1",
            "CV Macro-F1 SD",
            "Validation Macro-F1",
            "Validation Macro-Recall",
        ],
    ].copy()
    st.subheader("Baseline and selected model")
    st.dataframe(cv_validation, width="stretch", hide_index=True)

    st.subheader("All 14 experiment results")
    st.dataframe(experiments.drop(columns=["Configuration"]), width="stretch", hide_index=True)
    with st.expander("View the saved experiment configurations"):
        st.dataframe(
            experiments.loc[:, ["Experiment", "Model", "Configuration"]],
            width="stretch",
            hide_index=True,
        )

    selected = PROJECT_SUMMARY["selected_model"]
    st.info(
        f"Selected: {selected['name']}. It has the highest 3-fold CV Macro-F1 "
        f"({selected['cv_macro_f1']:.4f}) among the unique experiments. Its "
        f"Validation Macro-F1 is {selected['validation_macro_f1']:.4f}. "
        "The difference from the Random Forest baseline is small and has not "
        "been established as statistically significant."
    )

    assets = Path(__file__).resolve().parents[1] / "assets"
    with st.expander("Additional figures from the source experiments"):
        left, right = st.columns(2)
        learning_curve = assets / "decision_tree_learning_curve.png"
        mlp_loss = assets / "mlp_training_loss.png"
        e06_confusion = assets / "e06_validation_confusion_matrix.png"
        if learning_curve.is_file():
            left.image(
                str(learning_curve),
                caption="Decision Tree baseline learning curve.",
                width="stretch",
            )
        if mlp_loss.is_file():
            right.image(
                str(mlp_loss),
                caption="MLP baseline training loss.",
                width="stretch",
            )
        if e06_confusion.is_file():
            st.image(
                str(e06_confusion),
                caption="Selected Random Forest confusion matrix on Validation.",
                width="stretch",
            )
