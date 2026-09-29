# One-step, 50-channel smoke test ONLY

A one-epoch run with `--max-batches 1` on four synthetic/example images was executed to confirm that the full-size 4,962,229-parameter candidate can train, write `.pth` and recover payload. It is not a usable trained steganography model. The correction MSE was worse than the uncorrected AMBTC baseline on this tiny fixture. The actual full-size one-step checkpoint is distributed separately only for engineering inspection, clearly labeled smoke-only. No training-derived paper metrics are supported.

A separate 60-step/epoch synthetic demo check (`SMOKE_ONLY_60ep_learning_check.csv`) confirmed real gradient updates and occasional training-MSE improvement, but the final validation MSE was still above its baseline. **Do not present it as a trained useful research model.**
