# Remaining tasks for research student (narrowly scoped)

Do **not** rebuild the full PPO/DQN/U-Net pipeline or create approximate published numbers.

1. Verify the package on your workstation: `make clean && make && make test && python3 targeted/run_checks.py`; supply command log and file hashes. **No need to rerun an already verified suite unless source changes.**
2. Manually confirm the printed p.14 Figure 8(b) orange bar is `11.90%`, and inspect the other eight labels against `paper_reported/figure8b_digitized_labels.csv`; note any mismatch with page screenshot.
3. Compare only Section 4.4, Figure 8(b), Tables 4/10/11, bibliography [28]/[29]/[36]/[37]/[39]. Keep two columns: printed value, original source available? Do not invent epoch or plotting explanations.
4. Deliver one 1–2 page `TARGETED_REVIEW.md` plus screenshot crops / checksum manifest. Note explicitly `ORIGINAL_NEURAL_CHECKPOINTS_NOT_AVAILABLE` if not found.

Any future genuine independent experiments must be stored in a separate `new_experiments/` folder with exact model hashes, dataset IDs, seeds and confusion counts; they must not overwrite `paper_reported/`.
