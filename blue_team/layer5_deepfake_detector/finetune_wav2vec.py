"""
Fine-tunes the pretrained wav2vec2 deepfake detector on edge-tts synthetic
audio + real human speech, so it learns edge-tts's specific synthesis
signature (which it missed on Samiksha's original 4 clips - see
notebooks/13).
"""

import json
import numpy as np
import soundfile as sf
from datasets import Dataset
from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

MODEL_NAME = "Gustking/wav2vec2-large-xlsr-deepfake-audio-classification"
MANIFEST_PATH = "blue_team/layer5_deepfake_detector/finetune_audio/manifest.jsonl"
OUTPUT_DIR = "blue_team/layer5_deepfake_detector/checkpoints/finetuned_v1"

LABEL2ID = {"real": 0, "fake": 1}
ID2LABEL = {0: "real", 1: "fake"}


def load_manifest():
    entries = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            entries.append(json.loads(line))
    return entries


def load_audio_array(example, feature_extractor):
    audio, sr = sf.read(example["path"])
    if audio.ndim > 1:
        audio = audio.mean(axis=1)  # mono

    target_sr = feature_extractor.sampling_rate  # 16000
    if sr != target_sr:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)

    inputs = feature_extractor(audio, sampling_rate=target_sr, return_tensors="np", padding="max_length", max_length=48000, truncation=True)
    example["input_values"] = inputs["input_values"][0]
    example["label"] = LABEL2ID[example["label"]]
    return example

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary")
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

def main():
    print("Loading manifest...")
    entries = load_manifest()
    train_entries, val_entries = train_test_split(
        entries, test_size=0.25, random_state=42,
        stratify=[e["label"] for e in entries]
    )
    print(f"Train: {len(train_entries)}, Val: {len(val_entries)}")

    print("Loading feature extractor and model...")
    feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
    model = AutoModelForAudioClassification.from_pretrained(
        MODEL_NAME, num_labels=2, label2id=LABEL2ID, id2label=ID2LABEL,
        ignore_mismatched_sizes=True,
    )

    # Freeze the wav2vec2 base encoder - with only ~9 training examples,
    # fine-tuning all ~300M params causes training collapse (verified:
    # first attempt predicted one class for everything, accuracy stuck at
    # 0.333, loss oscillating rather than converging). Only train the
    # small classification head on top.
    for param in model.wav2vec2.parameters():
        param.requires_grad = False
    print("Base encoder frozen - only training classification head.")

    train_dataset = Dataset.from_list(train_entries).map(lambda x: load_audio_array(x, feature_extractor))
    val_dataset = Dataset.from_list(val_entries).map(lambda x: load_audio_array(x, feature_extractor))

    train_dataset = train_dataset.remove_columns(["path", "text", "voice"])
    val_dataset = val_dataset.remove_columns(["path", "text", "voice"])

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=15,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=2,
        learning_rate=1e-4,
        weight_decay=0.01,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("\nStarting fine-tuning (frozen encoder, head-only - should be faster now)...")
    trainer.train()

    print("\nFinal evaluation on validation set:")
    metrics = trainer.evaluate()
    print(metrics)

    print(f"\nSaving fine-tuned model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    feature_extractor.save_pretrained(OUTPUT_DIR)
    print("Done.")


if __name__ == "__main__":
    main()