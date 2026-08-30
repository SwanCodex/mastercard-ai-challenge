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


st.header("Analyst View")


event_id = st.text_input(
    "Event ID",
    value="api-integration-001",
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
            "YES" if verdict["attack_caught"] else "NO",
        )

    st.subheader("Why Was This Event Flagged?")

    st.write(verdict["explanation"])

    st.subheader("Layer Breakdown")

    for layer in verdict["layer_scores"]:
        st.write(
            f"**{layer['layer_name']}** — "
            f"Score: {layer['score']:.2f} — "
            f"{'FLAGGED' if layer['flagged'] else 'CLEAR'}"
        )

        if layer.get("reason"):
            st.caption(layer["reason"])

except requests.HTTPError as error:
    if error.response.status_code == 404:
        st.warning("No verdict found for this event ID.")
    else:
        st.error("Unable to retrieve the verdict.")

except requests.RequestException:
    st.error(
        "Unable to connect to the SENTINEL orchestrator API."
    )