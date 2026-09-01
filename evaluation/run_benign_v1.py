import json
from datetime import datetime, timezone
from shared.schemas.attack_event import AttackEvent, ToolCall
from blue_team.fusion.risk_fusion import run_pipeline

with open("evaluation/benign_dataset_v1.json", encoding="utf-8") as f:
    cases = json.load(f)

results = []

for c in cases:
    tools = []

    if c["type"] == "shopping":
        tools = [
            ToolCall(tool_name="browse_product", arguments={"query": c["product"]}),
            ToolCall(tool_name="add_to_cart", arguments={
                "product_id": c["product"],
                "quantity": c["quantity"]
            })
        ]
        if c["address"]:
            tools.append(ToolCall(
                tool_name="checkout",
                arguments={"shipping_address": c["address"]}
            ))

    elif c["type"] == "invoice":
        tools = [
            ToolCall(tool_name="read_invoice", arguments={"invoice_id": c["id"]}),
            ToolCall(tool_name="verify_vendor", arguments={"vendor": "authorized"}),
            ToolCall(tool_name="pay", arguments={
                "amount": c.get("amount"),
                "beneficiary_account": c["account"]
            })
        ]

    event = AttackEvent(
        event_id=c["id"],
        timestamp=datetime.now(timezone.utc),
        track="track_a_agentic",
        user_instruction=c["instruction"],
        untrusted_input=c["input"],
        agent_reasoning_trace=f"Legitimate processing of: {c['instruction']}",
        tool_calls_made=tools,
        transaction_fields={
            "amount": c.get("amount"),
            "beneficiary_account": c["account"]
        } if c.get("amount") is not None else None,
        campaign_id="benign-eval-v1",
        round_number=1,
        attack_variant_id=c["id"],
        attack_succeeded_against_agent=False
    )

    v = run_pipeline(event)
    results.append(v)

    print(f"{c['id']} | {v.decision:8} | {v.fusion_score:.3f}")

fp = sum(v.decision != "approve" for v in results)

print("\n--- SUMMARY ---")
print(f"Cases: {len(results)}")
print(f"Approved: {len(results)-fp}")
print(f"Escalated: {fp}")
print(f"FPR: {fp/len(results)*100:.1f}%")
