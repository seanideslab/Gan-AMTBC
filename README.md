# GAN-PPO-AMBTC — versioned research software and independent pilot records

**PUBLIC RELEASE CANDIDATE — author review and editor coordination required before posting.**

This repository is linked to *Signal Processing: Image Communication* 148 (2026), article 117652, DOI 10.1016/j.image.2026.117652. This release corrects the *demonstration* and adds a separately labelled **new independent reconstruction**. It is not the original end-to-end PPO/DQN/U-Net/SRM-SRNet research pipeline and does **not** reproduce Tables 4, 5, 10 or 11, Figure 8(b), or the published PSNR/P_E values. Published numerical values in `paper_reported/` are historical transcriptions, not measured outputs.

**Start here:** `RELEASE_README.md` (scope, provenance, data rights, commands), `independent_reconstruction/pilot_40/README.md` (new trained checkpoint and validation), and `targeted/` (publication consistency audit). The original GitHub history should be preserved and a distinct tagged release created; this ZIP does not change the remote repository.


---

# GAN-PPO-AMBTC: corrected audit and DEMONSTRATION package (not full paper reproduction)

**Status:** This is a transparency-oriented repair of the uploaded C archive. It does **not** contain the published PPO/DQN/U-Net/SRM-SRNet model, its original five-seed training records, full 5000-image test split, or trained advanced steganalyzers. It must not be represented as a reproduction of the numerical results in *Signal Processing: Image Communication* 148 (2026), 117652, DOI 10.1016/j.image.2026.117652.

## Important changes
- Removed `src/export_ablation.c` which wrote paper table values as string literals; the historical values are now **read-only transcriptions** in `paper_reported/` with explicit provenance, not generated empirical results.
- Removed `src/train_stub.c` which fabricated a smooth training curve. No pretend training log is emitted.
- Replaced unconstrained per-block toy allocation with a deterministic **demo-only** global budget projection over action set {1,2,4,8}. It reports both target and achieved capacity, with representability to the nearest integer payload bit.
- Uses unique deterministic bitmap positions and a separate serialized AMBTC triplet + action-map sidecar for actual **bitmap-level recovery**, rather than always claiming zero errors without checking anything.
- Exposes `double_tanh_centered()` for an asymmetric center-zero variant and `double_tanh()` as a symmetric or centered utility. Neither is evidence of what was actually used in the published experiments.
- Fixed `example/` vs `examples/`, `weight/` vs `weights/`, and the broken originally hard-coded local split path. The new smoke workflow is tested.
- Adds a real detector inference *adapter* requiring externally supplied trusted TorchScript weights, and a raw-run aggregation script that refuses missing experiments.

## Build, test, and demonstration
```
make
make test
bin/gan_ppo_ambtc_infer example/lena_like_64.pgm results/example0p4.pgm 0.4 weight/policy_smoke.txt
bin/gan_ppo_ambtc_extract results/example0p4.pgm.ambtc results/example0p4.pgm.map results/recovered.bin
cmp results/example0p4.pgm.payload.bin results/recovered.bin
```
The `.pgm` is a **visualization of decompressed pixels**; the `.ambtc` sidecar is the actual demonstration compressed representation and `.map` is required to know per-block bit counts. Recovering the bitstream solely from a re-encoded `.pgm` is NOT claimed.

`policy_smoke.txt` is an untrained toy weight file. The C generator is a small deterministic bitmap/quantization demonstration, not a U-Net. `PSNR` and `global_SSIM` printed by C are measured on the example input and are **not directly comparable** with published data. The resulting `DEMO_NOT_PAPER` CSV is deliberately separated from publication transcriptions.

Use `reproduction/README.md` for actual detector evaluation and missing-asset inventory; use `CORRECTION_AUDIT.md` and `EDITOR_CORRECTION_REQUEST.md` before updating a journal-linked public repository.

## Provenance and licensing
The user-provided 64x64 demo PGM and toy weights came with the original archive. No BOSSbase, BOWS-2 or medical images are redistributed. Before making the repository public, confirm redistribution permission for any included images or models. The original 5000-image split cannot be reconstructed from the submitted empty split files.

**Publication-level addendum (v2):** see `audit/README.md` for figure/table consistency check and `verification/` for separate 12-run C demo evidence. These files do not reproduce original PPO/GAN performance.

**Targeted addendum (v3):** `targeted/` contains new read-only inventory, mathematical and publication consistency checks and specific reference corrections. Figure 8(b) final orange published-label transcription corrected from 11.09 to 11.90. No original neural model has been recovered.

**Archived lab parameter note (v4, internal recovery):** see `recovery/README.md`. It adds a provenance-marked configuration record, untrained PyTorch architecture-only scaffold and data inventory tooling; no original model checkpoint or new paper performance measurement is claimed. The old C demo config remains untouched.
