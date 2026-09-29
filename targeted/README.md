# Targeted publication and software audit — v3

This folder is an add-on to the corrected **C demonstration**. It does not purport to be the GAN-PPO-AMBTC model or reproduce Tables 4, 5, 10 or 11.

## What can run now

```bash
make clean && make && make test
python3 targeted/run_checks.py
python3 reproduction/figure8_audit.py
```

- `make test` checks C demo payload control and bitmap-level extraction on the included 64×64 sample, the numerical formula utility, and the deliberate refusal to aggregate missing raw runs.
- `targeted/run_checks.py` writes a JSON inventory and reports printed Figure 8(b)/Tables 4/11 discrepancies; values are publication transcriptions, **not measured model outputs**.
- `reproduction/score_torchscript.py` is an adapter which requires an externally supplied genuine trained detector and paired images. It does not include a PPO/U-Net generator or model checkpoints.

## What has changed from v2

The directly inspected publisher PDF page 14 says **11.90%** for Figure 8(b), epsilon 0.3 and 0.4 bpp. v2 mistakenly transcribed `11.09`. Corrected `paper_reported/figure8b_digitized_labels.csv` and regenerated cross-check. Existing student logs or MVR evidence are historical and not silently altered; this changes a *transcription of the published graphic*, not scientific measurement.

Original package and v2 snapshots must remain retrievable. New versions should be released as a new tag without rewriting existing GitHub history.

## Important distinctions

1. C demo proof: corrected 0.1/0.2/0.4 bpp requests and bitmap sidecar round-trip.
2. Equation analysis: demonstrates incompatibility of printed subtraction and a **candidate** well-behaved centered sum. Original PyTorch training expression is not available.
3. Publication cross-check: identifies conflicting printed cells. Does not select scientifically correct measurements.
4. Bibliography: verified replacement metadata for [36], [37], and [28]/[29]; unsupported MORSE entry [39] flagged for correction/removal pending an authentic source.

Do not distribute the publisher's PDF as part of this code archive. Confirm redistribution rights for demo imagery.
