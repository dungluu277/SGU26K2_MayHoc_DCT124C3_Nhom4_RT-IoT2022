import streamlit as st


st.set_page_config(
    page_title="RT-IoT2022",
    page_icon="📡",
    layout="wide",
)

navigation_pages = [
    (
        st.Page(
            "pages/0_Overview.py",
            title="Overview",
            icon="📡",
            default=True,
        ),
        "Overview",
        "📡",
    ),
    (
        st.Page(
            "pages/1_Attack_Detection.py",
            title="Attack Detection",
            icon="🛡️",
        ),
        "Attack Detection",
        "🛡️",
    ),
    (
        st.Page(
            "pages/2_Prediction_Analysis.py",
            title="Prediction Analysis",
            icon="📊",
        ),
        "Prediction Analysis",
        "📊",
    ),
    (
        st.Page(
            "pages/3_Model_Comparison.py",
            title="Model Comparison",
            icon="⚖️",
        ),
        "Model Comparison",
        "⚖️",
    ),
]
page = st.navigation([item[0] for item in navigation_pages], position="hidden")
with st.sidebar:
    for navigation_page, label, icon in navigation_pages:
        st.page_link(navigation_page, label=label, icon=icon)
    st.divider()

page.run()
