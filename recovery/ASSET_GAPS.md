# Items still needed to move from architecture scaffold to measured results

These are **evidence requirements**, not a request to fabricate substitutes:

1. Original PyTorch PPO actor/critic `state_dict`, generator weights and network definitions, DQN scheduler code, optimizer state, and the checkpoint's epoch/version.
2. True trained steganalysis model or documented feature extraction/classifier implementations (SRM, maxSRMd2, SRNet, ERANet, SiaStegNet); the current score adapter does not provide them.
3. Authentic SRM kernels and their provenance before enabling the frozen SRM front end.
4. Original BOSSbase/BOWS-2 file IDs, stable train/val/test split with original random seed, and permission to access datasets. A new split is not the original split.
5. Raw cover/stego pairs, message bits, payload maps, five-run logs and source plotting data behind Figure 8(b)/Tables 4, 5, 10, 11.
6. The exact Double-Tanh implementation and any channel/quantization rounding logic.

When a new candidate asset appears: record original path, timestamp, SHA-256, owner/source and intended experiment; inspect it in a separate environment and never relabel a freshly reconstructed artifact as a recovered original.
