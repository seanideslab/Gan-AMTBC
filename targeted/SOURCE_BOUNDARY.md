# Status of available evidence

**Original source:** The user-provided GitHub source archive has no authentic PPO/DQN/U-Net training code, no original neural checkpoints, no raw five-seed experiment records, no detector checkpoints and no actual BOSSbase held-out ID list. The repaired package includes a C demonstration and a generic TorchScript *evaluation adapter*, not the published trained method. `weight/policy_smoke.txt` is a toy fixture.

**No inference about the old failure mechanism:** The observed original 0.25 bpp ceiling arose in the demonstration path; it is not evidence of an SRNet-driven protective clipping policy. The corrected C demo's full-image budget projection is a new functional fix and not the learned PPO policy.

**No inference about figures:** Repeated printed values do not prove original run values. Neither an epoch-index shift nor a baseline-column mapping error has been demonstrated; the original plotting data were not supplied.

**No inference about formula:** C demo `double_tanh_centered()` is an independent, tested candidate and is not called by the embedding path. Do not claim the original GPU model used it.
