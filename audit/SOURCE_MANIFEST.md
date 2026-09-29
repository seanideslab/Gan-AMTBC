# Source provenance for v2 addendum

- Published article: `[2]Security-AMBTC-Compressed 0726.pdf`; SHA-256 `397aacd56546d49c10a2c2b8de6513d43bacc1433379b26574d4b3d223d52820`; used as visual/page-reference authority. Not bundled in this ZIP.
- Corrected demonstration base: `Gan-AMTBC_repaired_transparency_v1.zip`; SHA-256 `98331858803127f68da34ea25861deb7e34751da71726398b13e7bdf7c96284d`. Original archive kept unchanged.
- Student recheck: `MVR_RECHECK.zip`; SHA-256 `1bfe4f954f4d4538707731afb30a07729e0bfeb2586322e0ba59fae40a69dfd4`. Original student submission kept unchanged.
- Publication table values: read-only `paper_reported/` files from the earlier corrected demonstration archive. They are **not** independently reproduced measurements.
- Student functional-test data: exact `MVR_RECHECK/DEMO_RESULTS.csv`, `DEMO_OUTPUTS/`, `INPUT_IMAGES/` in the student ZIP, copied into `verification/`. Original Windows command logs remain in original recheck ZIP and were not repackaged because they contain local user file paths.
- Linux `make test`: independently rerun for software functionality only; log at `verification/TEST_LOG_LINUX.txt`.

No original PyTorch training weights/code, held-out BOSSbase split, detector checkpoints, five-seed results, or chart source data have been recovered in this release.
