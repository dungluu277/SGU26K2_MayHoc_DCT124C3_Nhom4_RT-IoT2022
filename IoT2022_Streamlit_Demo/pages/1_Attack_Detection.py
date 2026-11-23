import io

import pandas as pd
import streamlit as st

from src.demo_utils import (
    DATA_DIR,
    load_manifest,
    predict_frame,
    prepare_features,
    render_header,
    safe_load_model,
    traffic_group,
)


render_header(
    "Attack Detection",
    "Validate flow features and run offline inference with the saved Random Forest.",
)

st.warning(
    "Offline batch inference only. This app is not connected to a live network "
    "and does not perform automated security response."
)
st.caption(
    "Provide the model's 82 input features. Attack_type is optional and is "
    "used only to calculate metrics for labeled rows."
)

source = st.radio(
    "Input source",
    ["Upload CSV", "Bundled sample"],
    horizontal=True,
    key="detection_input_source",
)
uploaded = None
frame = None
input_name = None

if source == "Upload CSV":
    uploaded = st.file_uploader(
        "Upload flow records",
        type=["csv"],
        key="detection_csv_upload",
        help="CSV must include all 82 model features; Attack_type may be included for evaluation.",
    )
    if uploaded is not None:
        active_key = f"upload:{uploaded.file_id}"
        input_name = uploaded.name
else:
    active_key = "bundled-sample"
    input_name = "sample_flows.csv"

if source == "Upload CSV" and uploaded is None:
    active_key = None

previous_key = st.session_state.get("active_detection_input")
if previous_key != active_key:
    for key in (
        "latest_predictions",
        "latest_metrics",
        "latest_confusion_matrix",
        "latest_has_labels",
        "latest_prediction_input",
    ):
        st.session_state.pop(key, None)
    st.session_state["active_detection_input"] = active_key

if uploaded is not None:
    try:
        frame = pd.read_csv(io.BytesIO(uploaded.getvalue()))
    except (
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        OSError,
        ValueError,
    ) as error:
        st.error(f"Could not read the uploaded CSV: {error}")
elif source == "Bundled sample":
    sample_path = DATA_DIR / "sample_flows.csv"
    try:
        frame = pd.read_csv(sample_path)
    except (
        FileNotFoundError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        OSError,
        ValueError,
    ) as error:
        st.error(f"Could not read the included sample file: {error}")
else:
    st.info("Upload a CSV file to continue.")

features = None
labels = None
extra_columns = []
schema_valid = False

if frame is not None:
    with st.container(border=True):
        st.markdown(f"**{input_name}**")
        cards = st.columns(3)
        cards[0].metric("Uploaded rows", f"{len(frame):,}")
        cards[1].metric("CSV columns", f"{len(frame.columns):,}")
        cards[2].metric("Expected model features", "82")
        st.caption("Preview of the uploaded records")
        st.dataframe(frame.head(6), width="stretch", hide_index=True)

    try:
        manifest = load_manifest()
        features, labels, extra_columns = prepare_features(frame, manifest)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as error:
        st.error(f"Input schema is not ready for prediction: {error}")
    else:
        schema_valid = True
        st.success(
            f"Schema valid · {len(features.columns)} features · "
            f"{len(features):,} rows"
        )
        if extra_columns:
            st.caption(
                "Additional columns are ignored by the model: "
                + ", ".join(extra_columns)
            )
        if labels is None:
            st.caption(
                "No Attack_type column found. Predictions will be shown without "
                "uploaded-data evaluation metrics."
            )
        else:
            st.caption(
                f"Ground-truth labels found for evaluation · {labels.nunique()} "
                "known classes in this file."
            )

if frame is not None and schema_valid:
    if st.button(
        "Analyze Network Traffic",
        type="primary",
        help="Run the saved model once for the current CSV.",
    ):
        model = safe_load_model()
        if model is not None:
            try:
                with st.spinner("Analyzing flows with the fitted pipeline..."):
                    predictions, metrics, matrix = predict_frame(
                        model, features, labels
                    )
            except (KeyError, TypeError, ValueError) as error:
                st.error(f"Prediction could not be completed: {error}")
            else:
                combined = pd.concat(
                    [
                        frame.reset_index(drop=True),
                        predictions.reset_index(drop=True),
                    ],
                    axis=1,
                )
                combined.insert(0, "Flow ID", range(1, len(combined) + 1))
                if labels is not None:
                    combined["Traffic_group_actual"] = [
                        traffic_group(str(label)) for label in labels
                    ]
                st.session_state["latest_predictions"] = combined
                st.session_state["latest_metrics"] = metrics
                st.session_state["latest_confusion_matrix"] = matrix
                st.session_state["latest_has_labels"] = labels is not None
                st.session_state["latest_prediction_input"] = active_key

latest = st.session_state.get("latest_predictions")
if (
    active_key is not None
    and st.session_state.get("latest_prediction_input") == active_key
    and isinstance(latest, pd.DataFrame)
    and not latest.empty
):
    st.subheader("Prediction summary")
    total = len(latest)
    attack_count = int((latest["Traffic_group_predicted"] == "Attack").sum())
    benign_count = total - attack_count
    with st.container(border=True):
        cards = st.columns(4)
        cards[0].metric("Flows analyzed", f"{total:,}")
        cards[1].metric("Predicted attacks", f"{attack_count:,}")
        cards[2].metric("Predicted benign", f"{benign_count:,}")
        cards[3].metric("Predicted attack share", f"{attack_count / total:.1%}")
    st.caption(
        "Attack/Benign groups use the project's verified label mapping. "
        "The maximum class vote is not a calibrated probability of real-world risk."
    )

    st.subheader("Flow-level results")
    filter_columns = st.columns(2)
    selected_class = filter_columns[0].selectbox(
        "Filter by predicted class",
        ["All classes"] + sorted(latest["Attack_type_predicted"].unique()),
    )
    selected_group = filter_columns[1].selectbox(
        "Filter by traffic group",
        ["All groups", "Attack", "Benign"],
    )
    visible = latest
    if selected_class != "All classes":
        visible = visible.loc[visible["Attack_type_predicted"] == selected_class]
    if selected_group != "All groups":
        visible = visible.loc[visible["Traffic_group_predicted"] == selected_group]

    display_columns = [
        "Flow ID",
        "Attack_type_predicted",
        "Traffic_group_predicted",
        "max_class_vote",
    ]
    if "Attack_type" in visible.columns:
        display_columns.append("Attack_type")
    table = visible.loc[:, display_columns].rename(
        columns={
            "Attack_type_predicted": "Predicted class",
            "Traffic_group_predicted": "Traffic group",
            "max_class_vote": "Max class vote",
            "Attack_type": "Actual label",
        }
    )
    st.caption(f"Showing {len(visible):,} of {total:,} analyzed flows.")
    st.dataframe(table, width="stretch", hide_index=True, height=360)

    selected_flow = st.number_input(
        "Inspect flow by row number",
        min_value=1,
        max_value=total,
        value=1,
        step=1,
    )
    flow = latest.iloc[[int(selected_flow) - 1]]
    with st.container(border=True):
        st.markdown(f"**Flow {int(selected_flow)}**")
        cards = st.columns(3)
        cards[0].metric("Predicted class", str(flow["Attack_type_predicted"].iloc[0]))
        cards[1].metric(
            "Traffic group", str(flow["Traffic_group_predicted"].iloc[0])
        )
        cards[2].metric(
            "Max class vote", f"{flow['max_class_vote'].iloc[0]:.2%}"
        )
        if "Attack_type" in flow.columns:
            st.caption(f"Uploaded ground truth: {flow['Attack_type'].iloc[0]}")
        attribute_columns = [
            column
            for column in (
                "proto",
                "service",
                "flow_duration",
                "id.orig_p",
                "id.resp_p",
            )
            if column in flow.columns
        ]
        if attribute_columns:
            st.dataframe(
                flow.loc[:, attribute_columns]
                .T.astype(str)
                .rename(columns={flow.index[0]: "Value"}),
                width="stretch",
            )
        with st.expander("View all model input features for this flow"):
            st.dataframe(
                flow.loc[:, features.columns]
                .T.astype(str)
                .rename(columns={flow.index[0]: "Value"}),
                width="stretch",
            )

    if st.session_state.get("latest_has_labels"):
        metrics = st.session_state.get("latest_metrics") or {}
        st.subheader("Evaluation on uploaded labeled rows")
        cards = st.columns(4)
        cards[0].metric("Accuracy", f"{metrics['accuracy']:.4f}")
        cards[1].metric("Macro-F1", f"{metrics['macro_f1']:.4f}")
        cards[2].metric("Macro-Recall", f"{metrics['macro_recall']:.4f}")
        cards[3].metric("Macro-Precision", f"{metrics['macro_precision']:.4f}")
        st.caption(
            "These metrics describe only the uploaded labeled rows; they are "
            "not the group's original held-out Test results."
        )

    csv_bytes = latest.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download all predictions as CSV",
        csv_bytes,
        file_name="rt_iot2022_predictions.csv",
        mime="text/csv",
    )
    st.success("Predictions are available on the Prediction Analysis page.")

with st.expander("Model input and label details"):
    st.write("The fitted model expects 82 features: 80 numeric fields and the categorical fields proto and service.")
    st.write(
        "Verified benign classes: MQTT_Publish, Thing_Speak and Wipro_bulb. "
        "The remaining nine RT-IoT2022 classes are mapped to Attack."
    )
