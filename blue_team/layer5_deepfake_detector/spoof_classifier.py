"""
Layer 5 - Audio Deepfake Detector
Uses a pretrained wav2vec2-based model fine-tuned specifically for
deepfake/spoofed audio detection.
"""
import os
import imageio_ffmpeg

_ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
_ffmpeg_dir = os.path.dirname(_ffmpeg_exe)

os.environ["PATH"] = (
    _ffmpeg_dir
    + os.pathsep
    + os.environ.get("PATH", "")
)

from transformers import pipeline

from shared.schemas.verdict import LayerScore
from shared.schemas.attack_event import AttackEvent

MODEL_NAME = "blue_team/layer5_deepfake_detector/layer5_finetuned_v1"
_classifier = pipeline("audio-classification", model=MODEL_NAME)

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("audio-classification", model=MODEL_NAME)
    return _classifier


def classify_audio(audio_path: str) -> dict:
    """
    Runs the deepfake classifier on an audio file.
    Returns the model top prediction: {label, score}.
    """
    classifier = get_classifier()
    results = classifier(audio_path)
    return results[0]


def score_event(event: AttackEvent) -> LayerScore:
    """
    Wraps classify_audio() to work with an AttackEvent, matching the
    same pattern as Layers 1-4.
    """
    if not event.audio_file_path:
        return LayerScore(
            layer_name="layer5_deepfake_detector",
            score=0.0,
            flagged=False,
            reason="no audio provided",
        )

    result = classify_audio(event.audio_file_path)
    label = result["label"].lower()
    confidence = result["score"]

    is_fake = "fake" in label or "spoof" in label
    suspicion_score = confidence if is_fake else (1 - confidence)
    flagged = suspicion_score >= 0.5

    return LayerScore(
        layer_name="layer5_deepfake_detector",
        score=suspicion_score,
        flagged=flagged,
        reason=f"model predicted '{label}' with confidence {confidence:.2f}",
    )


if __name__ == "__main__":
    test_files = [
        "red_team/track_b_deepfake_vishing/logs/audio/B01-v1.mp3",
        "red_team/track_b_deepfake_vishing/logs/audio/B01-v2.mp3",
        "red_team/track_b_deepfake_vishing/logs/audio/B02-v1.mp3",
        "red_team/track_b_deepfake_vishing/logs/audio/B03-v1.mp3",
    ]

    for f in test_files:
        result = classify_audio(f)
        print(f"{f}: {result}")