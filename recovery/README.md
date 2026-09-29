# Archived-note recovery addendum (v4) — architecture and data provenance

**STATUS: PARTIAL LAB-NOTE RECONSTRUCTION, NOT ORIGINAL TRAINING CODE OR PAPER REPRODUCTION.**

This addendum integrates a one-page older lab parameter summary supplied on 2026-09-29. Its original date and whether a later version exists are unknown. The PDF contains parameter statements and explicit architectural *estimates*, **not** network definitions, learned parameters, optimizer state, original split IDs, SRM coefficients, or five-seed records.

## What is genuinely new
- `recovered_note_profile.json` preserves the known numbers and flags unresolved fields.
- `recovered_vs_paper.csv` compares note, publication and old C demo. **Published Table 7b confirms batch size 16**; the `configs/default.cfg` batch size 8 belongs to the older demonstration and remains intact for traceability.
- `architecture_scaffold.py` supplies working, **randomly initialized architecture examples**: PPO actor–critic (shared and separate variants), DQN, a four-level U-Net-shaped module, and an SRM filter loader **that requires genuine kernels**. Shape/gradient tests can run. These are **not** the training, embedding or detection modules described in the paper.
- `dataset_inventory.py` creates SHA-256 image inventory from legally obtained data; optional `--new-split` is explicitly labeled **NEW**, groups byte-identical images together, and never claims to reconstruct the original 5,000-image test set.
- `asset_inventory.py` searches a user-supplied folder and hashes files; checkpoints remain unverified until source and contents can be established.

## Architecture-only smoke tests
```
python3 recovery/architecture_report.py
python3 -m unittest discover -s recovery -p 'test_*.py' -v
```
These checks need torch, numpy and Pillow; they do not train or evaluate the published GAN-PPO model. No neural checkpoint is generated.

## Dataset provenance (run only with authorized images)
```
python3 recovery/dataset_inventory.py --image-root /path/to/images --out-dir /path/to/report
# Optional NEW experiment split only:
python3 recovery/dataset_inventory.py --image-root /path/to/images --out-dir /path/to/report --new-split --seed 2026
python3 recovery/asset_inventory.py --search-root /path/to/old_lab_disk --out /path/to/asset_inventory.json
```
Do not upload restricted benchmark images or an internal full-disk inventory to a public repository.

## Important disagreements/unknowns
1. **PPO shared or separate:** the paper says shared two-layer actor–critic backbone; a simple shared 2x256 version has 67,845 parameters, while separate networks have 134,405. Neither proves the paper's approximate 0.12M model. The scaffold exposes both instead of pretending one is original.
2. **U-Net 4.87M:** the archive estimates channels 32,64,128,256, but omits precise block and feedback-channel topology. The illustrative network here has 1,926,243 parameters. Its outputs are *uncalibrated maps*, not valid stego triplets or a trained U-Net. It must not be tuned solely to match the reported count.
3. **DQN weight mapping:** archive mentions lambda1/lambda3; paper mentions lambda1 and co-adjusted lambda2/lambda3. The output action meaning and security-preferring bias are not reconstructed.
4. **Double-Tanh:** the note's alpha=10,beta=5,tau=.5 match paper parameters, **not** the original training equation. The published subtraction is inconsistent; the centered sum is a new mathematically well-behaved candidate, not an identified original implementation.
5. **SRM:** shape `[30,1,5,5]` and `requires_grad=False` are implementable, but coefficients and trained SRNet are absent. No fabricated random SRM filter bank is supplied.
6. **Epochs/batch/TTUR:** 200 and batch 16 are reported; ratio 4 is reported but exact training schedule and original absolute learning rates are not recovered from the note.

**Do not present this as a replacement for the original Python code or evidence for any Table 4/5/10/11 result.**

## Additional folder recovered note

See [`SECOND_FOLDER_NOTE.md`](SECOND_FOLDER_NOTE.md) for the **unverified Attention ResUNet .pth shape fingerprint** and 12 **candidate-only** BOSSbase split configurations. These supplement, rather than replace, the v4 architecture sketch.
