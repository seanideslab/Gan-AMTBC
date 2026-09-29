# Independent new PyTorch training lane (v6)

`new_training/` adds a documented NEW research reconstruction based on archived notes. It has never been represented as the recovered training code from the published 2026 paper.

- Old C demo, source audits, and publication transcription data are preserved from v5.
- The trained component is a new bitmap-preserving, one-channel quantization-compensation candidate. It is neither a recovered end-to-end GAN nor a replacement for original measurements.
- A separate PPO quality/budget-only trainer is available; no DQN or SRNet/SRM security component is represented as trained.
- Running the smoke test yields only `smoke_only=true` weights; real images with documented splits are required for a useful independent training experiment.
- Do not copy numbers from this project into published Table 4/5/10/11 or Figure 8(b).

Read `new_training/README.md` before running or uploading anything.
