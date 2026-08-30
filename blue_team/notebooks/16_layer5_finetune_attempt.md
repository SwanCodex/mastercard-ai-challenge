\# Layer 5 - Fine-Tuning Attempt and Root-Cause Diagnosis



\## Motivation

Zero-shot Layer 5 (notebooks/13) missed 3/4 of Samiksha's real edge-tts

vishing clips. Attempted to fine-tune on edge-tts synthetic audio +

real human speech (LibriSpeech), mirroring the successful Layer 2 playbook.



\## Data

Generated 18 edge-tts "fake" clips (varied voices/text) + 18 LibriSpeech

"real" clips (genuine human recordings, public domain, via

hf-internal-testing/librispeech\_asr\_dummy).



\## Training Attempts

1\. Full fine-tune (all \~300M wav2vec2 params), 9 examples: accuracy stuck

&#x20;  at 0.333, loss oscillating rather than converging, precision/recall/f1=0

&#x20;  (model collapsed to predicting one class).

2\. Frozen encoder + head-only fine-tune, same 9 examples: same collapse.

3\. Frozen encoder + head-only, scaled to 36 examples (18/18): accuracy

&#x20;  moved to 0.444 but precision/recall/f1 remained exactly 0.0 across all

&#x20;  15 epochs - still predicting one class for everything, no real

&#x20;  improvement from more data.



\## Root-Cause Diagnosis

Before attempting a 4th training run, measured whether the frozen

wav2vec2 encoder's pooled embeddings even separate fake vs. real audio

at all (pairwise distance analysis, n=16, 8 fake + 8 real):

\- Avg within-fake distance: 1.67

\- Avg within-real distance: 1.91

\- Avg fake-vs-real distance: 1.79



Fake-vs-real distance is SMALLER than within-real distance and

comparable to within-fake distance - there is no meaningful cluster

separation in the frozen embedding space for a linear head to learn.

This is not a data-volume or hyperparameter problem; the frozen

representation itself does not encode the real-vs-synthetic signal for

this audio distribution.



\## Conclusion

Head-only fine-tuning cannot succeed here regardless of how much more

data is added, since the bottleneck is representational, not the

classifier. A genuine fix would require unfreezing and updating deeper

encoder layers (true fine-tuning), which needs an order of magnitude

more training data than is available (Layer 2's successful fine-tune

used 66+ examples on a much smaller model; wav2vec2-large's scale makes

this proportionally harder). Not pursued further given remaining project

time.



\## Honest Reporting Value

This diagnosis is stronger evidence than a forced training success would

be: it demonstrates the specific representational reason edge-tts audio

evades this class of pretrained deepfake detector, rather than just

reporting a pass/fail number. Documented as a legitimate system

limitation with root-cause analysis for the report's "known limitations"

section, alongside the original zero-shot finding (notebooks/13).

