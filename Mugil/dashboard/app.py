"""
Streamlit dashboard for the
Autonomous Retail Supply Chain Recovery Agent.

The dashboard is a presentation layer.
Agent/business logic should remain in the backend.
"""

import streamlit as st


st.set_page_config(
    page_title="Retail Supply Chain Recovery",
    layout="wide"
)


def main():
    st.title("🚚 Autonomous Retail Supply Chain Recovery Agent")
    st.caption("Evaluation, verification and recovery monitoring")

    # --------------------------------------------------
    # Recovery Goal
    # --------------------------------------------------

    st.header("Recovery Goal")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Required Quantity", "—")

    with col2:
        st.metric("Deadline", "— hours")

    with col3:
        st.metric("Maximum Cost", "—")

    with col4:
        st.metric("Carbon Limit", "— kg CO₂e")

    st.divider()

    # --------------------------------------------------
    # Current Situation
    # --------------------------------------------------

    st.header("Current Situation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📦 Inventory")
        st.info("Waiting for Environment data")

    with col2:
        st.subheader("🚚 Shipment")
        st.info("Waiting for Environment data")

    with col3:
        st.subheader("⚠️ Disruption")
        st.info("No disruption data received")

    st.divider()

    # --------------------------------------------------
    # Alternatives and Selected Action
    # --------------------------------------------------

    st.header("Recovery Decision")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Available Alternatives")
        st.info("Waiting for Planner data")

    with col2:
        st.subheader("Selected Action")
        st.info("Waiting for Controller data")

    st.divider()

    # --------------------------------------------------
    # Execution Status
    # --------------------------------------------------

    st.header("Execution Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Action ID", "—")

    with col2:
        st.metric("Execution", "Waiting")

    with col3:
        st.metric("System Decision", "—")

    st.divider()

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    st.header("Verification")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Quantity", "—")

    with col2:
        st.metric("Delivery Time", "— hours")

    with col3:
        st.metric("Cost", "—")

    with col4:
        st.metric("Carbon", "— kg CO₂e")

    st.divider()

    # --------------------------------------------------
    # Final Outcome
    # --------------------------------------------------

    st.header("Final Outcome")

    st.info(
        "Waiting for evaluation result from the backend."
    )

    # --------------------------------------------------
    # Activity Timeline
    # --------------------------------------------------

    st.header("Activity Timeline")

    timeline = [
        "Goal received",
        "Recovery planning",
        "Action selected",
        "Execution",
        "Verification",
        "Final outcome"
    ]

    for step in timeline:
        st.write(f"• {step} — waiting")

    st.divider()

    st.caption(
        "Dashboard is connected to the evaluation layer during integration."
    )


if __name__ == "__main__":
    main()