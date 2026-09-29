# Release candidate — correction and provenance, 2026-09-29

## Three distinct evidence classes

1. **Repaired C demonstration:** `src/`, `verification/`, `tests/`. Fixed global payload budgeting and actual bitmap-level extraction; not a PPO/U-Net full inference pipeline. Old hard-coded result exporter and synthetic train logger are removed. Demonstration performance never equals paper-performance evidence.
2. **New independently reconstructed pilot:** `new_training/` and `independent_reconstruction/pilot_40/`. CandidateAttentionResUNet, base=50, 4,962,229 parameters, newly initialized, 3 epochs on **40 newly selected BOSSbase images**, 64x64 resized. Best checkpoint is included. No trained SRNet, DQN reward scheduler, original PPO-GAN joint experiment or measured P_E. New pilot PSNR is versus AMBTC cover and not comparable to 40.35 dB in the paper.
3. **Historical publication and correction audit:** `paper_reported/`, `targeted/`, `audit/`. Figure and table numbers are transcriptions, not reproduced measurements. Figure 8(b) conflicting values remain unresolved; do not generate a replacement figure without independent evidence/editor agreement.

## Fixed-validation facts (new small pilot, NOT original paper)

- Source: BOSSbase 1.01, independent seed-42 selection. 20 train, 10 validation, 10 holdout; the source images are **not included**.
- Best checkpoint: `independent_reconstruction/pilot_40/checkpoint_best.pth`, SHA-256 `dcbb6440dd1db5f70240c48013e6d3feed7faaf693a4e122276eb9231a944639`.
- Fixed-validation epochs: 1/2/3 and independent per-image records in `independent_reconstruction/pilot_40/`.
- Holdout: 0.2 bpp achieved 0.19995117, +0.0949 dB PSNR versus AMBTC cover, 0 bit errors; 0.4 bpp achieved 0.39990234, +0.1054 dB, 0 bit errors. These are 10 holdout images and a pilot experiment, not a five-seed 5,000-image reproduction.
- Original benchmark raw images not redistributed. See portable filename+SHA-256 manifest and official source URL. Confirm redistribution rights independently before uploading images. Original publication train/test split and source checkpoint remain unavailable.

## Reproducing from authorized input images

Install Python requirements in `new_training/requirements.txt`; obtain BOSSbase from the official download source and locate the **40 selected files** in `dataset_manifest_portable.json`, verifying their SHA-256 values. Use `new_training/train_generator.py` and `new_training/evaluate_new.py` with the copied source version. The original student training logs record one run but include Windows absolute paths; this public manifest deliberately replaces those machine-specific paths. Exact command-line flags are documented in `new_training/README.md` and `independent_reconstruction/pilot_40/evidence/METHODS_AND_REPRODUCIBILITY.md`.

`checkpoint_best.pth` is a PyTorch weights-only load candidate from a new independent experiment: inspect the SHA-256 and load from trusted origin with `torch.load(..., map_location='cpu', weights_only=True)` before use. Do not mistake it for an archived original model.

## Known gaps

Original PyTorch end-to-end model/checkpoints, 5,000-image original split list, five independent runs, detector weights for SRM/maxSRMd2/SRNet/ERANet/SiaStegNet and Figure 8(b) raw data remain unavailable. The reader must not infer published security results from the new pilot. For release status, contact the article's corresponding author / publisher correction notice.

## Data provenance and licences

BOSSbase is a third-party benchmark; this release contains only image IDs, SHA-256 manifest, scripts, results and our new trained model. The publication PDF is not bundled. The original historical public repository is preserved via Git history / versioned tag, not erased.
