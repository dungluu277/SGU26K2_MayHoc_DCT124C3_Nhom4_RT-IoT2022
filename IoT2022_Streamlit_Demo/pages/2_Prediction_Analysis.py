import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import classification_report

from src.demo_utils import PROJECT_SUMMARY, load_local_csv, render_header


render_header(
    "Prediction Analysis",
    "Explore class distribution, individual flows and labeled evaluation results.",
)

latest = st.session_state.get("latest_predictions")
if isinstance(latest, pd.DataFrame) and not latest.empty:
    total = len(latest)
    class_counts = (
        latest["Attack_type_predicted"]
        .value_counts()
        .rename_axis("Predicted class")
        .reset_index(name="Flows")
    )
    group_counts = (
        latest["Traffic_group_predicted"]
        .value_counts()
        .rename_axis("Traffic group")
        .reset_index(name="Flows")
    )
    attack_count = int((latest["Traffic_group_predicted"] == "Attack").sum())
    benign_count = total - attack_count

    st.subheader("Most recent prediction")
    with st.container(border=True):
        cards = st.columns(4)
        cards[0].metric("Flows analyzed", f"{total:,}")
        cards[1].metric("Predicted attacks", f"{attack_count:,}")
        cards[2].metric("Predicted benign", f"{benign_count:,}")
        cards[3].metric("Predicted attack share", f"{attack_count / total:.1%}")

    chart_columns = st.columns([1.5, 1, 1])
    class_chart = px.bar(
        class_counts.sort_values("Flows", ascending=True),
        x="Flows",
        y="Predicted class",
        orientation="h",
        color_discrete_sequence=["#1E3A5F"],
        labels={"Flows": "Predicted flows"},
    )
    class_chart.update_layout(
        height=440,
        margin=dict(l=12, r=12, t=18, b=12),
        yaxis=dict(title=None, automargin=True),
        xaxis=dict(gridcolor="#E2E8F0"),
        showlegend=False,
    )
    chart_columns[0].plotly_chart(
        class_chart, width="stretch", config={"displayModeBar": False}
    )

    group_chart = px.pie(
        group_counts,
        names="Traffic group",
        values="Flows",
        hole=0.58,
        color="Traffic group",
        color_discrete_map={"Attack": "#1E3A5F", "Benign": "#3B82F6"},
    )
    group_chart.update_layout(
        height=360,
        margin=dict(l=8, r=8, t=18, b=8),
        legend_title_text="",
    )
    chart_columns[1].plotly_chart(
        group_chart, width="stretch", config={"displayModeBar": False}
    )

    if "max_class_vote" in latest.columns:
        vote_chart = px.histogram(
            latest,
            x="max_class_vote",
            nbins=20,
            color_discrete_sequence=["#3B82F6"],
            labels={"max_class_vote": "Maximum class vote"},
        )
        vote_chart.update_layout(
            height=360,
            margin=dict(l=8, r=8, t=18, b=12),
            xaxis=dict(range=[0, 1], gridcolor="#E2E8F0"),
            yaxis=dict(title="Flows", gridcolor="#E2E8F0"),
            showlegend=False,
        )
        chart_columns[2].plotly_chart(
            vote_chart, width="stretch", config={"displayModeBar": False}
        )

    st.caption(
        "The maximum class vote is the model's highest class score, not a "
        "calibrated probability of real-world attack risk."
    )
    st.dataframe(class_counts, width="stretch", hide_index=True)

    st.subheader("Inspect an individual flow")
    row_number = st.number_input(
        "Flow row",
        min_value=1,
        max_value=total,
        value=1,
        step=1,
        key="analysis_flow_row",
    )
    selected = latest.iloc[[int(row_number) - 1]]
    with st.container(border=True):
        cards = st.columns(4)
        cards[0].metric("Flow ID", str(selected["Flow ID"].iloc[0]))
        cards[1].metric(
            "Predicted class", str(selected["Attack_type_predicted"].iloc[0])
        )
        cards[2].metric(
            "Traffic group", str(selected["Traffic_group_predicted"].iloc[0])
        )
        cards[3].metric(
            "Maximum class vote",
            f"{selected['max_class_vote'].iloc[0]:.2%}",
        )
        if "Attack_type" in selected.columns:
            st.caption(f"Uploaded ground truth: {selected['Attack_type'].iloc[0]}")
        details = [
            column
            for column in (
                "proto",
                "service",
                "flow_duration",
                "id.orig_p",
                "id.resp_p",
            )
            if column in selected.columns
        ]
        if details:
            st.dataframe(
                selected.loc[:, details]
                .T.astype(str)
                .rename(columns={selected.index[0]: "Value"}),
                width="stretch",
            )
        with st.expander("View all model input features"):
            excluded = {
                "Flow ID",
                "Attack_type",
                "Traffic_group_actual",
                "Attack_type_predicted",
                "Traffic_group_predicted",
                "max_class_vote",
            }
            model_features = [
                column
                for column in selected.columns
                if column not in excluded and not column.startswith("probability_")
            ]
            st.dataframe(
                selected.loc[:, model_features]
                .T.astype(str)
                .rename(columns={selected.index[0]: "Value"}),
                width="stretch",
            )

    labeled = (
        bool(st.session_state.get("latest_has_labels"))
        and "Attack_type" in latest.columns
    )
    if labeled:
        metrics = st.session_state.get("latest_metrics") or {}
        st.subheader("Evaluation on uploaded labeled data")
        with st.container(border=True):
            cards = st.columns(4)
            cards[0].metric("Accuracy", f"{metrics['accuracy']:.4f}")
            cards[1].metric("Macro-F1", f"{metrics['macro_f1']:.4f}")
            cards[2].metric("Macro-Recall", f"{metrics['macro_recall']:.4f}")
            cards[3].metric("Macro-Precision", f"{metrics['macro_precision']:.4f}")
        st.caption(
            "These metrics are calculated only because this upload included "
            "Attack_type ground truth."
        )

        matrix = st.session_state.get("latest_confusion_matrix")
        if isinstance(matrix, pd.DataFrame):
            st.subheader("Confusion matrix")
            matrix_display = st.selectbox(
                "Matrix values",
                ["Counts", "Row-normalized"],
                help="Row normalization expresses each actual class as proportions.",
            )
            if matrix_display == "Row-normalized":
                row_totals = matrix.sum(axis=1).astype(float)
                row_totals = row_totals.mask(row_totals == 0)
                matrix_values = (
                    matrix.astype(float).div(row_totals, axis=0).fillna(0.0)
                )
                text_format = ".2f"
                color_label = "Row proportion"
            else:
                matrix_values = matrix
                text_format = True
                color_label = "Count"
            confusion_chart = px.imshow(
                matrix_values,
                text_auto=text_format,
                aspect="auto",
                color_continuous_scale="Blues",
                labels={
                    "x": "Predicted class",
                    "y": "Actual class",
                    "color": color_label,
                },
            )
            confusion_chart.update_layout(
                height=610,
                margin=dict(l=8, r=8, t=18, b=8),
            )
            st.plotly_chart(
                confusion_chart, width="stretch", config={"displayModeBar": False}
            )

        st.subheader("Classification report")
        report = pd.DataFrame(
            classification_report(
                latest["Attack_type"].astype(str),
                latest["Attack_type_predicted"].astype(str),
                output_dict=True,
                zero_division=0,
            )
        ).T
        report.index.name = "Class"
        st.dataframe(report, width="stretch")

        st.subheader("Misclassified flows")
        errors = latest.loc[
            latest["Attack_type"].astype(str)
            != latest["Attack_type_predicted"].astype(str)
        ].copy()
        if errors.empty:
            st.success("No misclassified flows in this labeled upload.")
        else:
            reverse_pair = (
                (
                    (errors["Attack_type"] == "Thing_Speak")
                    & (errors["Attack_type_predicted"] == "ARP_poisioning")
                )
                | (
                    (errors["Attack_type"] == "ARP_poisioning")
                    & (errors["Attack_type_predicted"] == "Thing_Speak")
                )
            )
            pair_count = int(reverse_pair.sum())
            if pair_count:
                st.info(
                    f"{pair_count} observed confusion(s) between Thing_Speak "
                    "and ARP_poisioning in this upload."
                )
            pairs = sorted(
                set(
                    zip(
                        errors["Attack_type"].astype(str),
                        errors["Attack_type_predicted"].astype(str),
                    )
                )
            )
            selected_pair = st.selectbox(
                "Filter actual → predicted class pair",
                [None] + pairs,
                format_func=lambda pair: (
                    "All misclassifications"
                    if pair is None
                    else f"{pair[0]} → {pair[1]}"
                ),
            )
            if selected_pair is not None:
                errors = errors.loc[
                    (errors["Attack_type"] == selected_pair[0])
                    & (errors["Attack_type_predicted"] == selected_pair[1])
                ]
            error_columns = [
                column
                for column in (
                    "Flow ID",
                    "Attack_type",
                    "Traffic_group_actual",
                    "Attack_type_predicted",
                    "Traffic_group_predicted",
                    "max_class_vote",
                )
                if column in errors.columns
            ]
            st.caption(f"{len(errors):,} misclassified flows match this filter.")
            st.dataframe(
                errors.loc[:, error_columns].rename(
                    columns={
                        "Attack_type": "Actual class",
                        "Traffic_group_actual": "Actual group",
                        "Attack_type_predicted": "Predicted class",
                        "Traffic_group_predicted": "Predicted group",
                        "max_class_vote": "Max class vote",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
    else:
        st.info(
            "This prediction has no ground-truth Attack_type labels. Class "
            "counts and flow details are available, but evaluation metrics, "
            "confusion matrix and misclassification analysis are not."
        )
else:
    st.info(
        "No current prediction is available. Run Analyze Network Traffic on "
        "the Attack Detection page to populate this analysis."
    )

with st.expander("Reported held-out Test results from the group report"):
    st.caption(
        "This is a separate, saved evaluation result—not a score for the "
        "current upload. Values are not recomputed from unlabeled predictions."
    )
    summary = PROJECT_SUMMARY["selected_model"]["test"]
    cards = st.columns(4)
    cards[0].metric("Test accuracy", f"{summary['accuracy']:.4f}")
    cards[1].metric("Test Macro-F1", f"{summary['macro_f1']:.4f}")
    cards[2].metric("Test Macro-Recall", f"{summary['macro_recall']:.4f}")
    cards[3].metric(
        "Correct Test predictions", f"{summary['correct']:,} / {summary['rows']:,}"
    )
    try:
        per_class = load_local_csv("test_per_class.csv")
        confusion_data = load_local_csv("test_confusion_matrix.csv")
    except FileNotFoundError as error:
        st.error(f"Saved source evaluation results are missing: {error}")
    else:
        if "Class" in per_class.columns:
            chart_data = per_class.loc[per_class["Class"] != "Macro avg"]
            report_chart = px.bar(
                chart_data.sort_values("F1", ascending=True),
                x="F1",
                y="Class",
                orientation="h",
                hover_data=["Recall", "Precision", "Support"],
                range_x=[0, 1.05],
                color_discrete_sequence=["#1E3A5F"],
                labels={"F1": "F1 score"},
            )
            report_chart.update_layout(
                height=460,
                margin=dict(l=8, r=8, t=18, b=8),
                yaxis=dict(title=None, automargin=True),
                xaxis=dict(gridcolor="#E2E8F0"),
                showlegend=False,
            )
            st.plotly_chart(
                report_chart, width="stretch", config={"displayModeBar": False}
            )
            st.dataframe(per_class, width="stretch", hide_index=True)

        confusion = confusion_data.set_index(confusion_data.columns[0])
        st.plotly_chart(
            px.imshow(
                confusion,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                labels={"x": "Predicted", "y": "Actual", "color": "Count"},
            ),
            width="stretch",
            config={"displayModeBar": False},
        )
    st.warning(
        "The Test set includes very few Metasploit_Brute_Force_SSH (5) and "
        "NMAP_FIN_SCAN (4) examples. Their per-class scores are unstable and "
        "should not be interpreted as a guarantee of attack detection."
    )
