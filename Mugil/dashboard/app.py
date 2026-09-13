"""
Premium Streamlit dashboard for the
Autonomous Retail Supply Chain Recovery Agent.

Presentation layer connected to the real integrated recovery flow.
"""

import streamlit as st


# ============================================================
# BACKEND IMPORTS
# ============================================================

from Nisar.agent.adapters import (
    MugilVerifierAdapter,
    PavanExecutorAdapter,
    PreetheshSelectorAdapter,
)

from Nisar.agent.contracts import (
    CurrentState,
    InventoryLevel,
)

from Nisar.agent.controller import (
    RecoveryController,
)

from Nisar.agent.monitor import (
    Monitor,
)

from Pavan.environment import (
    Environment,
)

from Pavan.executor import (
    Executor,
)

from Preethesh.tools.alternatives import (
    AlternativeGenerator,
    AlternativeSelector,
)

from Mugil.evaluation.evaluator import (
    evaluate_result,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Autonomous Supply Chain Recovery",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HTML RENDER HELPER
# ============================================================

def render_html(content):
    """
    Remove leading whitespace from every HTML line so
    Streamlit does not interpret the HTML as Markdown code.
    """

    cleaned = "\n".join(
        line.lstrip()
        for line in content.splitlines()
    )

    st.markdown(
        cleaned,
        unsafe_allow_html=True,
    )


# ============================================================
# PREMIUM CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
background:
radial-gradient(
circle at 10% 10%,
rgba(0,120,255,0.10),
transparent 30%
),
radial-gradient(
circle at 90% 20%,
rgba(0,255,180,0.08),
transparent 30%
),
#080b12;

color:#f5f7fb;
}


.main .block-container {
max-width:1450px;

padding-top:2rem;
padding-bottom:4rem;
}


p,
span,
div {
font-family:
Inter,
-apple-system,
BlinkMacSystemFont,
"Segoe UI",
sans-serif;
}


/* ==========================================================
HERO
========================================================== */

.hero {

padding:2.2rem 2.4rem;

border-radius:24px;

border:1px solid rgba(255,255,255,0.08);

background:
linear-gradient(
135deg,
rgba(25,35,55,0.95),
rgba(10,15,25,0.98)
);

box-shadow:
0 20px 60px rgba(0,0,0,0.35),
inset 0 1px 0 rgba(255,255,255,0.04);

margin-bottom:1.5rem;
}


.hero-title {

font-size:2.9rem;

font-weight:850;

line-height:1.05;

margin-bottom:0.7rem;

color:#f7f9fc;
}


.hero-subtitle {

color:#9da8ba;

font-size:1.05rem;

line-height:1.6;
}


.live-pill {

display:inline-block;

margin-top:1.2rem;

padding:0.45rem 0.85rem;

border-radius:999px;

background:
rgba(25,200,120,0.12);

border:
1px solid rgba(25,200,120,0.25);

color:#42e69b;

font-size:0.85rem;

font-weight:700;
}


/* ==========================================================
SECTION LABEL
========================================================== */

.section-label {

margin-top:2rem;

margin-bottom:1rem;

color:#7f8ba0;

font-size:0.78rem;

font-weight:800;

letter-spacing:0.13em;

text-transform:uppercase;
}


/* ==========================================================
KPI CARDS
========================================================== */

.kpi-card {

min-height:135px;

padding:1.25rem;

border-radius:18px;

background:
linear-gradient(
145deg,
rgba(25,34,50,0.95),
rgba(13,18,28,0.95)
);

border:
1px solid rgba(255,255,255,0.07);

box-shadow:
0 12px 35px rgba(0,0,0,0.22);
}


.kpi-label {

color:#8995a8;

font-size:0.82rem;

font-weight:650;

text-transform:uppercase;

letter-spacing:0.08em;
}


.kpi-value {

margin-top:0.5rem;

font-size:2rem;

font-weight:800;

color:#f7f9fc;
}


.kpi-small {

margin-top:0.3rem;

color:#718096;

font-size:0.8rem;
}


/* ==========================================================
DISRUPTION
========================================================== */

.disruption-card {

padding:1.5rem 1.7rem;

border-radius:20px;

background:
linear-gradient(
135deg,
rgba(130,65,20,0.30),
rgba(45,28,18,0.75)
);

border:
1px solid rgba(255,155,60,0.22);
}


.disruption-title {

color:#ffb45c;

font-size:1.1rem;

font-weight:800;
}


.disruption-text {

margin-top:0.5rem;

color:#d7dce5;

font-size:1rem;

line-height:1.6;
}


/* ==========================================================
PIPELINE
========================================================== */

.pipeline {

display:flex;

align-items:center;

justify-content:center;

gap:0.7rem;

margin:1.5rem 0 2rem;

flex-wrap:wrap;
}


.agent {

min-width:200px;

padding:1.25rem;

text-align:center;

border-radius:18px;

background:
linear-gradient(
145deg,
rgba(24,34,52,0.95),
rgba(13,18,28,0.95)
);

border:
1px solid rgba(255,255,255,0.08);

box-shadow:
0 10px 30px rgba(0,0,0,0.18);

transition:
transform 0.2s ease,
border 0.2s ease;
}


.agent:hover {

transform:translateY(-4px);

border:
1px solid rgba(80,160,255,0.35);
}


.agent-icon {

font-size:2rem;
}


.agent-name {

margin-top:0.4rem;

font-weight:800;

color:#f4f7fb;

font-size:1rem;
}


.agent-role {

margin-top:0.25rem;

color:#8490a3;

font-size:0.78rem;
}


.agent-status {

margin-top:0.7rem;

color:#45e69d;

font-size:0.75rem;

font-weight:800;
}


.arrow {

color:#506079;

font-size:1.8rem;

font-weight:700;
}


/* ==========================================================
ACTION CARD
========================================================== */

.action-card {

padding:1.5rem;

border-radius:20px;

background:
linear-gradient(
135deg,
rgba(30,55,80,0.85),
rgba(14,22,34,0.95)
);

border:
1px solid rgba(70,150,255,0.15);

box-shadow:
0 12px 35px rgba(0,0,0,0.18);
}


.action-id {

font-size:1.5rem;

font-weight:850;

color:#ffffff;
}


.action-type {

margin-top:0.3rem;

color:#55a7ff;

font-weight:700;
}


.action-description {

margin-top:0.8rem;

color:#aeb8c8;

line-height:1.5;
}


/* ==========================================================
SUCCESS
========================================================== */

.success-card {

margin-top:1.5rem;

padding:2.5rem;

border-radius:24px;

text-align:center;

background:
radial-gradient(
circle at center,
rgba(35,190,120,0.15),
transparent 65%
),
linear-gradient(
145deg,
rgba(15,50,38,0.95),
rgba(8,24,19,0.98)
);

border:
1px solid rgba(50,230,150,0.22);

box-shadow:
0 20px 60px rgba(0,0,0,0.3);
}


.success-icon {

font-size:3rem;
}


.success-title {

margin-top:0.5rem;

font-size:2rem;

font-weight:850;

color:#48e89e;
}


.success-subtitle {

margin-top:0.5rem;

color:#a7b4aa;

font-size:1rem;
}


/* ==========================================================
TIMELINE
========================================================== */

.timeline {

margin-top:1rem;

padding:1.5rem;

border-radius:20px;

background:
rgba(14,20,30,0.88);

border:
1px solid rgba(255,255,255,0.07);
}


.timeline-item {

display:flex;

align-items:center;

gap:1rem;

padding:0.85rem 0;

color:#dfe5ee;

border-bottom:
1px solid rgba(255,255,255,0.04);
}


.timeline-item:last-child {

border-bottom:none;
}


.timeline-check {

display:inline-flex;

align-items:center;

justify-content:center;

width:28px;

height:28px;

border-radius:50%;

background:
rgba(40,220,140,0.12);

color:#43e69a;

font-weight:900;

flex-shrink:0;
}


/* ==========================================================
BUTTON
========================================================== */

div.stButton > button {

width:100%;

min-height:58px;

border:0;

border-radius:16px;

font-size:1.05rem;

font-weight:800;

background:
linear-gradient(
135deg,
#1677ff,
#6757ff
);

color:white;

box-shadow:
0 12px 30px rgba(35,95,255,0.25);

transition:
all 0.2s ease;
}


div.stButton > button:hover {

transform:translateY(-2px);

box-shadow:
0 16px 35px rgba(35,95,255,0.35);
}


/* ==========================================================
INFO BOX
========================================================== */

div[data-testid="stAlert"] {

border-radius:16px;
}


/* ==========================================================
FOOTER
========================================================== */

.footer {

text-align:center;

margin-top:2.5rem;

color:#566174;

font-size:0.78rem;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BUILD EVALUATION REQUEST
# ============================================================

def build_evaluation_request(
    goal,
    plan,
    execution,
):

    evidence = dict(
        execution.execution_evidence
    )

    result = evidence.get(
        "result",
        {},
    )

    if not isinstance(
        result,
        dict,
    ):
        result = {}

    constraints = dict(
        goal.constraints
    )

    if "shortfall_quantity" in constraints:

        constraints["required_quantity"] = (
            constraints["shortfall_quantity"]
        )

    expected = {
        key: constraints[key]
        for key in (
            "required_quantity",
            "deadline",
            "max_cost",
            "budget",
            "carbon_limit",
        )
        if key in constraints
    }

    return {

        "action_id":
            execution.action_id,

        "goal":
            goal,

        "expected":
            expected,

        "actual": {

            "delivered_quantity":
                result.get(
                    "delivered_quantity"
                ),

            "delivery_time":
                result.get(
                    "delivery_time"
                ),

            "total_cost":
                result.get(
                    "total_cost"
                ),

            "carbon_emission":
                result.get(
                    "carbon_emission"
                ),
        },
    }


# ============================================================
# REAL AUTONOMOUS RECOVERY
# ============================================================

def run_real_recovery():

    initial_state = CurrentState(

        snapshot_id="dashboard-demo",

        inventory=(
            InventoryLevel(
                "SKU-001",
                2,
                5,
            ),
        ),

        shipments=(),

        demand=(),
    )


    class ShortageSource:

        def get_current_state(
            self
        ):
            return initial_state


    monitor = Monitor(
        ShortageSource()
    )


    supplier_getter = (
        lambda item_id, location: [

            {
                "action_id":
                    "purchase-1",

                "supplier_id":
                    "supplier-1",

                "status":
                    "available",

                "capacity":
                    100,
            }

        ]
    )


    route_getter = (
        lambda item_id, location: []
    )


    generator = (
        AlternativeGenerator()
    )


    raw_selector = AlternativeSelector(

        generator,

        supplier_getter,

        route_getter,
    )


    selector = (
        PreetheshSelectorAdapter(
            raw_selector
        )
    )


    environment = (
        Environment()
    )


    pavan = Executor(
        environment
    )


    executor = (
        PavanExecutorAdapter(
            pavan.execute_step
        )
    )


    verifier = (
        MugilVerifierAdapter(

            evaluate_result,

            build_evaluation_request,
        )
    )


    controller = RecoveryController(

        monitor=monitor,

        alternative_selector=selector,

        executor=executor,

        verifier=verifier,

        max_replanning_attempts=2,

        recovery_location="warehouse",
    )


    outcome = controller.recover()


    return (
        outcome,
        environment,
    )


# ============================================================
# KPI HELPER
# ============================================================

def render_kpi(
    label,
    value,
    subtitle="",
):

    render_html(
        f"""
        <div class="kpi-card">

        <div class="kpi-label">
        {label}
        </div>

        <div class="kpi-value">
        {value}
        </div>

        <div class="kpi-small">
        {subtitle}
        </div>

        </div>
        """
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # HERO
    # ========================================================

    render_html(
        """
        <div class="hero">

        <div class="hero-title">
        🚚 Autonomous Supply Chain Recovery
        </div>

        <div class="hero-subtitle">
        Intelligent disruption detection, recovery planning,
        execution and verification
        </div>

        <div class="live-pill">
        ● LIVE INTEGRATED SYSTEM
        </div>

        </div>
        """
    )


    # ========================================================
    # CONTROL CENTER
    # ========================================================

    if "result" not in st.session_state:

        render_html(
            """
            <div class="section-label">
            CONTROL CENTER
            </div>
            """
        )

        st.info(
            "Ready to simulate a real supply-chain "
            "disruption and run autonomous recovery."
        )


    # ========================================================
    # RUN BUTTON
    # ========================================================

    if st.button(
        "🚀  RUN AUTONOMOUS RECOVERY"
    ):

        with st.spinner(
            "AI agents are coordinating the recovery..."
        ):

            try:

                outcome, environment = (
                    run_real_recovery()
                )

                st.session_state[
                    "result"
                ] = outcome

                st.session_state[
                    "environment"
                ] = environment

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Recovery execution failed: {exc}"
                )

                st.exception(exc)


    # ========================================================
    # RESULT
    # ========================================================

    result = st.session_state.get(
        "result"
    )

    environment = st.session_state.get(
        "environment"
    )


    if result is None:

        render_html(
            """
            <div class="footer">

            Autonomous Retail Supply Chain Recovery Agent

            </div>
            """
        )

        return


    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    render_html(
        """
        <div class="section-label">
        SYSTEM OVERVIEW
        </div>
        """
    )


    constraints = dict(
        result.goal.constraints
    )


    required_quantity = constraints.get(
        "shortfall_quantity",

        constraints.get(
            "required_quantity",
            3,
        ),
    )


    action = result.action


    history = (

        environment.get_history()

        if environment is not None

        else []
    )


    latest = (

        history[-1]

        if history

        else {}
    )


    if not isinstance(
        latest,
        dict,
    ):
        latest = {}


    execution_result = latest.get(
        "result",
        latest,
    )


    if not isinstance(
        execution_result,
        dict,
    ):
        execution_result = {}


    delivered = execution_result.get(
        "delivered_quantity",
        "—",
    )


    delivery_time = execution_result.get(
        "delivery_time",
        "—",
    )


    total_cost = execution_result.get(
        "total_cost",
        "—",
    )


    carbon = execution_result.get(
        "carbon_emission",
        "—",
    )


    # ========================================================
    # KPI ROW
    # ========================================================

    cols = st.columns(4)


    with cols[0]:

        render_kpi(
            "RECOVERY TARGET",

            required_quantity,

            "units required",
        )


    with cols[1]:

        render_kpi(
            "DELIVERED",

            delivered,

            "units recovered",
        )


    with cols[2]:

        render_kpi(

            "RECOVERY COST",

            (
                f"₹{total_cost}"

                if total_cost != "—"

                else "—"
            ),

            "execution cost",
        )


    with cols[3]:

        render_kpi(

            "CARBON",

            (
                f"{carbon} kg"

                if carbon != "—"

                else "—"
            ),

            "CO₂e emissions",
        )


    # ========================================================
    # DISRUPTION
    # ========================================================

    render_html(
        """
        <div class="section-label">
        DISRUPTION DETECTED
        </div>

        <div class="disruption-card">

        <div class="disruption-title">
        ⚠️ Inventory Shortage
        </div>

        <div class="disruption-text">
        SKU-001 has insufficient inventory.
        Current stock is <b>2 units</b> while
        <b>5 units</b> are required.
        </div>

        </div>
        """
    )


    # ========================================================
    # AUTONOMOUS PIPELINE
    # ========================================================

    render_html(
        """
        <div class="section-label">
        AUTONOMOUS RECOVERY PIPELINE
        </div>

        <div class="pipeline">


        <div class="agent">

        <div class="agent-icon">
        🧠
        </div>

        <div class="agent-name">
        Controller
        </div>

        <div class="agent-role">
        Goal Detection & Decision
        </div>

        <div class="agent-status">
        ✓ COMPLETE
        </div>

        </div>


        <div class="arrow">
        →
        </div>


        <div class="agent">

        <div class="agent-icon">
        🧩
        </div>

        <div class="agent-name">
        Recovery Planner
        </div>

        <div class="agent-role">
        Alternative Selection
        </div>

        <div class="agent-status">
        ✓ COMPLETE
        </div>

        </div>


        <div class="arrow">
        →
        </div>


        <div class="agent">

        <div class="agent-icon">
        ⚙️
        </div>

        <div class="agent-name">
        Execution Engine
        </div>

        <div class="agent-role">
        Recovery Action
        </div>

        <div class="agent-status">
        ✓ COMPLETE
        </div>

        </div>


        <div class="arrow">
        →
        </div>


        <div class="agent">

        <div class="agent-icon">
        🛡️
        </div>

        <div class="agent-name">
        Verification Engine
        </div>

        <div class="agent-role">
        Result Validation
        </div>

        <div class="agent-status">
        ✓ COMPLETE
        </div>

        </div>


        </div>
        """
    )


    # ========================================================
    # RECOVERY DECISION
    # ========================================================

    render_html(
        """
        <div class="section-label">
        RECOVERY DECISION
        </div>
        """
    )


    col1, col2 = st.columns(2)


    with col1:

        render_html(
            """
            <div class="action-card">

            <div class="kpi-label">
            AVAILABLE ALTERNATIVE
            </div>

            <div class="action-id">
            purchase-1
            </div>

            <div class="action-type">
            Supplier available
            </div>

            <div class="action-description">
            Supplier-1 can provide the required inventory.
            </div>

            </div>
            """
        )


    with col2:

        action_id = (

            action.action_id

            if action

            else "—"
        )


        operation = (

            action.operation

            if action

            else "—"
        )


        description = (

            action.description

            if action

            else "No action selected."
        )


        render_html(
            f"""
            <div class="action-card">

            <div class="kpi-label">
            SELECTED ACTION
            </div>

            <div class="action-id">
            {action_id}
            </div>

            <div class="action-type">
            {operation}
            </div>

            <div class="action-description">
            {description}
            </div>

            </div>
            """
        )


    # ========================================================
    # EXECUTION STATUS
    # ========================================================

    render_html(
        """
        <div class="section-label">
        EXECUTION STATUS
        </div>
        """
    )


    cols = st.columns(3)


    with cols[0]:

        render_kpi(

            "ACTION ID",

            (
                action.action_id

                if action

                else "—"
            ),

            "selected recovery action",
        )


    with cols[1]:

        render_kpi(

            "EXECUTION",

            "SUCCESS",

            "execution engine",
        )


    with cols[2]:

        render_kpi(

            "SYSTEM DECISION",

            result.status.value.upper(),

            "controller outcome",
        )


    # ========================================================
    # VERIFICATION
    # ========================================================

    render_html(
        """
        <div class="section-label">
        VERIFICATION
        </div>
        """
    )


    cols = st.columns(4)


    with cols[0]:

        render_kpi(

            "QUANTITY",

            delivered,

            "delivered successfully",
        )


    with cols[1]:

        render_kpi(

            "DELIVERY",

            (
                f"{delivery_time}h"

                if delivery_time != "—"

                else "—"
            ),

            "delivery time",
        )


    with cols[2]:

        render_kpi(

            "COST",

            (
                f"₹{total_cost}"

                if total_cost != "—"

                else "—"
            ),

            "execution cost",
        )


    with cols[3]:

        render_kpi(

            "CARBON",

            (
                f"{carbon} kg"

                if carbon != "—"

                else "—"
            ),

            "CO₂e emissions",
        )


    # ========================================================
    # FINAL OUTCOME
    # ========================================================

    if result.status.value == "recovered":

        render_html(
            """
            <div class="success-card">

            <div class="success-icon">
            🟢
            </div>

            <div class="success-title">
            RECOVERY SUCCESSFUL
            </div>

            <div class="success-subtitle">
            The autonomous agent recovered the supply-chain
            disruption and verified the result.
            </div>

            </div>
            """
        )

    else:

        st.error(
            f"Recovery outcome: {result.status.value}"
        )


    # ========================================================
    # ACTIVITY TIMELINE
    # ========================================================

    render_html(
        """
        <div class="section-label">
        ACTIVITY TIMELINE
        </div>

        <div class="timeline">


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Goal received
        </b>

        <span>
        Recovery requirement identified
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Disruption detected
        </b>

        <span>
        Inventory shortage identified
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Recovery planning
        </b>

        <span>
        Alternative supplier evaluated
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Action selected
        </b>

        <span>
        purchase-1 selected
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Execution
        </b>

        <span>
        Recovery action executed
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Verification
        </b>

        <span>
        Quantity, delivery, cost and carbon checked
        </span>

        </div>


        <div class="timeline-item">

        <span class="timeline-check">
        ✓
        </span>

        <b>
        Final outcome
        </b>

        <span>
        System recovered successfully
        </span>

        </div>


        </div>
        """
    )


    # ========================================================
    # FOOTER
    # ========================================================

    render_html(
        """
        <div class="footer">

        Autonomous Retail Supply Chain Recovery Agent

        &nbsp; • &nbsp;

        Autonomous Detection · Planning · Execution · Verification

        </div>
        """
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()