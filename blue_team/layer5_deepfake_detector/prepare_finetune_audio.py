"""
Prepares a fine-tuning dataset for Layer 5: additional edge-tts synthetic
("fake") clips + real human speech clips from LJSpeech ("real"), so the
detector learns edge-tts's specific synthesis signature rather than only
the more exotic deepfake methods it was pretrained on.
"""

import asyncio
import os
import json

import edge_tts
from datasets import load_dataset

FAKE_DIR = "blue_team/layer5_deepfake_detector/finetune_audio/fake"
REAL_DIR = "blue_team/layer5_deepfake_detector/finetune_audio/real"
MANIFEST_PATH = "blue_team/layer5_deepfake_detector/finetune_audio/manifest.jsonl"

os.makedirs(FAKE_DIR, exist_ok=True)
os.makedirs(REAL_DIR, exist_ok=True)

# Varied text, different voices/styles than Samiksha's 4 originals,
# still plausible vishing-style phrasing so the domain matches.
FAKE_TEXTS = [
    ("en-US-GuyNeural", "Hi, this is IT support calling about your account. I need you to confirm the verification code you just received."),
    ("en-US-JennyNeural", "This is a courtesy call from your bank. Your recent transaction has been flagged and requires immediate confirmation."),
    ("en-GB-RyanNeural", "Good afternoon, I'm calling to verify your identity for the payment authorization on file."),
    ("en-US-AriaNeural", "Hello, I already completed the security check with your colleague a few minutes ago, so we can skip that step."),
    ("en-AU-WilliamNeural", "This is a follow-up regarding your recent request. Please proceed with the transfer as discussed."),
    ("en-IN-PrabhatNeural", "Hi there, just confirming the one-time code so we can finalize your enrollment today."),
    ("en-US-GuyNeural", "Hi, this is IT support calling about your account. I need you to confirm the verification code you just received."),
    ("en-US-JennyNeural", "This is a courtesy call from your bank. Your recent transaction has been flagged and requires immediate confirmation."),
    ("en-GB-RyanNeural", "Good afternoon, I'm calling to verify your identity for the payment authorization on file."),
    ("en-US-AriaNeural", "Hello, I already completed the security check with your colleague a few minutes ago, so we can skip that step."),
    ("en-AU-WilliamNeural", "This is a follow-up regarding your recent request. Please proceed with the transfer as discussed."),
    ("en-IN-PrabhatNeural", "Hi there, just confirming the one-time code so we can finalize your enrollment today."),
    ("en-US-ChristopherNeural", "This is a routine verification call. Can you confirm your account number for me?"),
    ("en-GB-SoniaNeural", "I'm calling regarding a pending transaction that needs your immediate approval."),
    ("en-US-MichelleNeural", "Your identity has already been confirmed through our automated system, so we can proceed directly."),
    ("en-CA-ClaraNeural", "This is a final reminder to authorize the payment before the deadline today."),
    ("en-US-EricNeural", "I need to verify a few details before we can process your request."),
    ("en-GB-ThomasNeural", "Please hold while I connect you to update your account security settings."),

]


async def generate_fake_clips():
    manifest = []
    for i, (voice, text) in enumerate(FAKE_TEXTS, start=1):
        path = f"{FAKE_DIR}/synth_{i:02d}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)
        manifest.append({"path": path, "label": "fake", "text": text, "voice": voice})
        print(f"Generated: {path}")
    return manifest


def prepare_real_clips(n=6):
    print("Loading LibriSpeech dummy dataset (real human speech)...")
    from datasets import Audio
    ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
    ds = ds.select(range(min(n, len(ds))))
    # Disable the Audio() auto-decode feature (which needs torchcodec) and
    # instead read the raw bytes ourselves via soundfile - avoids the
    # torchcodec/FFmpeg native-library dependency entirely.
    ds = ds.cast_column("audio", Audio(decode=False))

    import soundfile as sf
    import io

    manifest = []
    for i, sample in enumerate(ds, start=1):
        audio_bytes = sample["audio"]["bytes"]
        path = f"{REAL_DIR}/real_{i:02d}.wav"

        data, samplerate = sf.read(io.BytesIO(audio_bytes))
        sf.write(path, data, samplerate)

        manifest.append({"path": path, "label": "real", "text": sample.get("text", ""), "voice": "librispeech_human"})
        print(f"Saved: {path}")
    return manifest

def main():
    fake_manifest = asyncio.run(generate_fake_clips())
    real_manifest = prepare_real_clips(n=len(FAKE_TEXTS))

    all_entries = fake_manifest + real_manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry) + "\n")

    print(f"\nManifest written: {len(all_entries)} entries ({len(fake_manifest)} fake, {len(real_manifest)} real)")


if __name__ == "__main__":
    main()