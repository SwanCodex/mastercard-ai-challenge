import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="SENTINEL Security Dashboard",
    page_icon="🛡️",
    layout="wide",
)


st.title("SENTINEL Security Dashboard")
st.caption("Adversarial payment-security monitoring and defense analytics")


campaign_id = st.text_input(
    "Campaign ID",
    value="api-integration-test",
)


def get_campaign_metrics(campaign_id: str):
    response = requests.get(
        f"{API_BASE_URL}/get_metrics/{campaign_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def compute_round_metrics(campaign_id: str):
    response = requests.get(
        f"{API_BASE_URL}/get_metrics/{campaign_id}",
        timeout=30,
    )
    response.raise_for_status()

    records_response = requests.get(
        f"{API_BASE_URL}/get_campaign_records/{campaign_id}",
        timeout=30,
    )
    records_response.raise_for_status()

    records = records_response.json()

    verdict_by_event_id = {
        verdict["event_id"]: verdict
        for verdict in records["verdicts"]
    }

    round_data = {}

    for event in records["attack_events"]:
        if not event["attack_succeeded_against_agent"]:
            continue

        verdict = verdict_by_event_id.get(event["event_id"])

        if verdict is None:
            continue

        round_number = event["round_number"]

        if round_number not in round_data:
            round_data[round_number] = {
                "attacks": 0,
                "caught": 0,
            }

        round_data[round_number]["attacks"] += 1

        if verdict["attack_caught"]:
            round_data[round_number]["caught"] += 1

    return {
        round_number: (
            values["caught"] / values["attacks"]
            if values["attacks"]
            else 0.0
        )
        for round_number, values in sorted(round_data.items())
    }

def get_campaign_records(campaign_id: str):
    response = requests.get(
        f"{API_BASE_URL}/get_campaign_records/{campaign_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_verdict(event_id: str):
    response = requests.get(
        f"{API_BASE_URL}/get_verdict/{event_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


st.header("Campaign Overview")


try:
    metrics = get_campaign_metrics(campaign_id)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Events",
            metrics["total_events"],
        )

    with col2:
        st.metric(
            "Attack Catch Rate",
            f"{metrics['attack_catch_rate']:.1%}",
        )

    with col3:
        st.metric(
            "False Positive Rate",
            f"{metrics['false_positive_rate']:.1%}",
        )

    with col4:
        st.metric(
            "Average Latency",
            f"{metrics['average_latency_ms']:.0f} ms",
        )

    st.subheader("Campaign Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric(
            "Attacks",
            metrics["attacks"],
        )

    with summary_col2:
        st.metric(
            "Caught Attacks",
            metrics["caught_attacks"],
        )

    with summary_col3:
        st.metric(
            "Missed Attacks",
            metrics["missed_attacks"],
        )

except requests.RequestException:
    st.error(
        "Unable to connect to the SENTINEL orchestrator API. "
        "Make sure the FastAPI server is running."
    )


st.header("Attack Success Rate Over Rounds")


try:
    round_metrics = compute_round_metrics(campaign_id)

    if round_metrics:
        chart_data = {
            "Round": list(round_metrics.keys()),
            "Attack Catch Rate": list(round_metrics.values()),
        }

        st.line_chart(
            chart_data,
            x="Round",
            y="Attack Catch Rate",
        )
    else:
        st.info(
            "No attack events with verdicts are available "
            "for this campaign."
        )

except requests.RequestException:
    st.error("Unable to retrieve round-level campaign data.")

st.subheader("Analyst View")

try:
    campaign_records = get_campaign_records(campaign_id)

    show_attacks_only = st.checkbox(
        "Show attack events only",
        value=True,
    )

    events = campaign_records["attack_events"]

    if show_attacks_only:
        events = [
            event
            for event in events
            if event["attack_succeeded_against_agent"]
        ]

    event_ids = [
        event["event_id"]
        for event in events
    ]

    if not event_ids:
        st.info("No events are available for this campaign.")
    else:
        event_id = st.selectbox(
            "Select Event",
            event_ids,
        )

        try:
            verdict = get_verdict(event_id)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Decision",
                    verdict["decision"].upper(),
                )

            with col2:
                st.metric(
                    "Fusion Risk",
                    f"{verdict['fusion_score']:.1%}",
                )

            with col3:
                st.metric(
                    "Attack Caught",
                    "YES"
                    if verdict["attack_caught"]
                    else "NO",
                )

            st.markdown("---")

            st.subheader("Why Was This Event Flagged?")

            st.write(
                verdict["explanation"]
            )

            st.subheader("Layer Breakdown")

            for layer in verdict["layer_scores"]:
                status = (
                    "FLAGGED"
                    if layer["flagged"]
                    else "CLEAR"
                )

                st.write(
                    f"**{layer['layer_name']}** — "
                    f"Score: {layer['score']:.2f} — "
                    f"{status}"
                )

                if layer.get("reason"):
                    st.caption(
                        layer["reason"]
                    )

            st.subheader("Event Details")

            selected_event = next(
                event
                for event in events
                if event["event_id"] == event_id
            )

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.write(
                    "**Track:** "
                    f"{selected_event['track']}"
                )

                st.write(
                    "**Attack Variant:** "
                    f"{selected_event['attack_variant_id']}"
                )

                st.write(
                    "**Round:** "
                    f"{selected_event['round_number']}"
                )

            with detail_col2:
                st.write(
                    "**Attack Succeeded Against Agent:** "
                    f"{'YES' if selected_event['attack_succeeded_against_agent'] else 'NO'}"
                )

                st.write(
                    "**Event ID:** "
                    f"{selected_event['event_id']}"
                )

                st.write(
                    "**Timestamp:** "
                    f"{selected_event['timestamp']}"
                )

            with st.expander("User Instruction"):
                st.write(
                    selected_event["user_instruction"]
                )

            if selected_event.get("untrusted_input"):
                with st.expander("Untrusted Input"):
                    st.write(
                        selected_event["untrusted_input"]
                    )

            if selected_event.get("agent_reasoning_trace"):
                with st.expander("Agent Reasoning Trace"):
                    st.write(
                        selected_event["agent_reasoning_trace"]
                    )

            if selected_event.get("tool_calls_made"):
                with st.expander("Tool Calls Made"):
                    st.json(
                        selected_event["tool_calls_made"]
                    )

        except requests.RequestException as exc:
            st.error(
                f"Unable to retrieve verdict: {exc}"
            )

except requests.RequestException as exc:
    st.error(
        f"Unable to retrieve campaign events: {exc}"
    )