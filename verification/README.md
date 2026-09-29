# C demonstration functional-check evidence

Copied from the student `MVR_RECHECK.zip` (unchanged values and bytes); checksums of input archive in `../audit/SOURCE_MANIFEST.md`. The 12 pairs are four 64x64 functional fixtures x three requested payloads. Extra fixtures are synthetic. Every row is marked `DEMO_NOT_PAPER`.

The `.ambtc` and `.map` sidecars are required for bitstream recovery. The `stego.pgm` is a decompressed visual preview, not a self-contained steganographic file. PSNR/global SSIM values are not the paper's metrics. The toy `policy_smoke.txt` is not a trained PPO checkpoint.

The student's full Windows run logs (including machine paths and environmental restrictions) remain in the separate original `MVR_RECHECK.zip`; they are deliberately not published here. `TEST_LOG_LINUX.txt` records an independent clean Linux build/test on the same corrected C source (not paper-model evaluation).
