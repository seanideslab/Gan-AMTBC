# NEW_INDEPENDENT_RECONSTRUCTION — pilot_40

Status: SMALL PILOT / SMOKE ONLY; not the published PPO-DQN-GAN experiment. Best weight SHA-256 `dcbb6440dd1db5f70240c48013e6d3feed7faaf693a4e122276eb9231a944639`.

- 40 independently sampled BOSSbase images: 20 train, 10 validation, 10 holdout; 512x512 original to 64x64 resize. Images not included. See `dataset_manifest_portable.*` for archive filenames + hashes.
- 3 epochs, batch 2, base=50 candidate Attention ResUNet, CPU; seed 42, no original checkpoint loaded.
- `results/` contains the per-epoch fixed validation and one-time holdout scores; `evidence/` contains method, source metadata, verification and selection records.
- Metrics are versus the AMBTC cover with [0,1] pixels. Bitmap-level extraction zero errors does not demonstrate recovery after converting the stego image to a generic image file.
- Weights in `checkpoint_best.pth` are from *this independent pilot only* and are **not** the original published GAN-PPO-AMBTC weights; the original five-seed paper results and detection error P_E are not reproduced.
