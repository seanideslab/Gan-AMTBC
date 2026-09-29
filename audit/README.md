# Figure/table consistency review addendum (v2)

This folder was added to the corrected **C demonstration** package after a student MVR recheck. It does **not** add the missing original PPO/DQN/U-Net training stack, original image split, five independent raw runs or trained steganalysis models.

- `STUDENT_NEXT_TASKS.md`: concise Traditional Chinese assignment, designed for the final publication-level figure/table check.
- `FIGURE_TABLE_MATRIX.md`: prefilled register of figures/tables and the corresponding published-page references.
- `FIG8B_PUBLICATION_CROSSCHECK.csv`: programmatically derived differences between published Figure 8(b) labels and published Tables 4/11. All records have status `PUBLICATION_TRANSCRIPTION_ONLY`; they are not experimental results.
- `check_fig8b_publication.py`: compares the existing read-only transcriptions under `paper_reported/` without model inference.
- `CHECK_LOG.txt`: output from that comparison.
- `SOURCE_MANIFEST.md`: exact source-archive/PDF checksums and provenance boundaries.
- `../verification/`: separate C demo outputs and testing evidence. **Never** use those PSNR/SSIM values as published full-model metrics.

The published PDF is **not redistributed** in this ZIP; provide `[2]Security-AMBTC-Compressed 0726.pdf` directly to the student for page-image verification and store screenshots in their internal evidence folder. The original versioned source archive and MVR_RECHECK.zip remain unchanged. Before public GitHub release, review embedded image/media redistribution rights and remove any internal-only evidence as needed.
