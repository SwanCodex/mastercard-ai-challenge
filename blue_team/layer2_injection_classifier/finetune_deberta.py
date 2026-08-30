"""
Fine-tunes ProtectAI's DeBERTa-v3 injection classifier on our
payments-specific attack payloads + benign examples.
"""

import json
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

MODEL_NAME = "protectai/deberta-v3-base-prompt-injection-v2"
DATA_PATH = "blue_team/layer2_injection_classifier/finetune_data.jsonl"
OUTPUT_DIR = "blue_team/layer2_injection_classifier/checkpoints/finetuned_v1"


def load_data():
    examples = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            examples.append(json.loads(line))
    return examples


def tokenize_function(examples, tokenizer):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary")
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


def main():
    print("Loading data...")
    examples = load_data()
    train_examples, val_examples = train_test_split(
        examples, test_size=0.2, random_state=42,
        stratify=[e["label"] for e in examples]
    )
    print(f"Train: {len(train_examples)}, Val: {len(val_examples)}")

    train_dataset = Dataset.from_list(train_examples)
    val_dataset = Dataset.from_list(val_examples)

    print("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    train_dataset = train_dataset.map(lambda x: tokenize_function(x, tokenizer), batched=True)
    val_dataset = val_dataset.map(lambda x: tokenize_function(x, tokenizer), batched=True)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=5,
        learning_rate=2e-5,
        weight_decay=0.01,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("\nStarting fine-tuning (this may take a while on CPU)...")
    trainer.train()

    print("\nFinal evaluation on validation set:")
    metrics = trainer.evaluate()
    print(metrics)

    print(f"\nSaving fine-tuned model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()