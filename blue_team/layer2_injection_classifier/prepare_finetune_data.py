"""
Prepares the fine-tuning dataset for Layer 2: combines Samiksha's 58 real
attack payloads (positive/INJECTION examples) with a set of benign
payments-related text (negative/SAFE examples), producing a balanced
dataset for fine-tuning.
"""

import json
import random

from blue_team.layer2_injection_classifier.payload_converter import load_all_track_a_events

# Benign, payments-related text - the model needs to see plenty of normal
# e-commerce/payment language so it doesn't just learn "any payment-related
# text = suspicious". These are hand-written to resemble real usage,
# spanning shopping, invoices, and general customer service interactions.
BENIGN_EXAMPLES = [
    "Blue cotton t-shirt, available in S/M/L. Ships in 2-3 business days.",
    "Please confirm the total amount before checkout.",
    "Can you check if my order has shipped yet?",
    "I'd like to update my billing address to 12 Park Lane.",
    "What's the status of my invoice payment?",
    "My card was declined, can you retry the payment?",
    "I want to cancel my subscription and get a refund.",
    "This laptop bag has a padded compartment and side pockets for accessories.",
    "Free shipping on orders over $50. Delivery within 5-7 days.",
    "Thank you for your purchase! Your order confirmation number is 48213.",
    "Wireless earbuds with 20-hour battery life and noise cancellation.",
    "Please process the invoice for vendor ABC Corp, amount $3,200.",
    "Can I get a receipt emailed to me for this purchase?",
    "The item is currently out of stock, expected back in 2 weeks.",
    "I'd like to apply my loyalty discount to this order.",
    "Your payment of $89.99 has been successfully processed.",
    "Please verify the vendor's bank details before releasing payment.",
    "Standard delivery takes 3-5 business days within the continental US.",
    "I need to return this item, it doesn't fit correctly.",
    "Can you split this payment across two cards?",
    "The invoice due date has been extended by 15 days per our agreement.",
    "This product comes with a 1-year manufacturer warranty.",
    "Please double-check the shipping address matches the billing address.",
    "I authorize payment of $450 to Acme Supplies for the March order.",
    "Customer service hours are Monday-Friday, 9am-6pm EST.",
]


def build_finetune_dataset(output_path="blue_team/layer2_injection_classifier/finetune_data.jsonl"):
    """
    Combines attack payloads (label=1, INJECTION) with benign examples
    (label=0, SAFE) into a single JSONL file ready for HuggingFace training.
    """
    attack_events = load_all_track_a_events()

    examples = []

    # Positive examples (attacks)
    for event in attack_events:
        if event.untrusted_input and event.untrusted_input.strip():
            examples.append({"text": event.untrusted_input, "label": 1})

    # Negative examples (benign)
    for text in BENIGN_EXAMPLES:
        examples.append({"text": text, "label": 0})

    random.seed(42)
    random.shuffle(examples)

    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    num_pos = sum(1 for e in examples if e["label"] == 1)
    num_neg = sum(1 for e in examples if e["label"] == 0)

    print(f"Dataset written to {output_path}")
    print(f"Total examples: {len(examples)}")
    print(f"Positive (INJECTION): {num_pos}")
    print(f"Negative (SAFE): {num_neg}")

    return examples


if __name__ == "__main__":
    build_finetune_dataset()