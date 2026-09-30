# GAN-PPO-AMBTC v1.2.0 — Release Notes

## Release status

Public transparency release. This version preserves the historical repository record and separates corrected software, newly generated pilot results, and transcriptions of published numerical values.

## Included materials

1. Corrected C embedding demonstration and functional tests.
2. Independent PyTorch reconstruction, including a newly trained candidate checkpoint.
3. A documented 40-image BOSSbase 1.01 pilot, with a 20/10/10 split.
4. Fixed-validation results for three epochs and per-image holdout records.
5. Standalone revised Figure 8(b) and its source CSV.
6. Publication consistency audits and source-provenance records.

## Independent pilot

The new pilot used 64 × 64 resized images, a base-50 candidate Attention ResUNet, batch size 2, three epochs, and seed 42.

Best checkpoint: epoch 3.

Checkpoint SHA-256:
dcbb6440dd1db5f70240c48013e6d3feed7faaf693a4e122276eb9231a944639

At 0.2 bpp, the 10-image holdout recorded a mean PSNR change of 23.8788 to 23.9738 dB.

At 0.4 bpp, the corresponding change was 23.4627 to 23.5681 dB.

Both comparisons use the AMBTC cover as reference. Bitmap-level extraction checks recorded zero errors.

These are new small-pilot results, not a reproduction of the published full-system experiment.

## Revised Figure 8(b)

The revised standalone panel presents the published Table 11 clipping-sensitivity values at 0.4 bpp. The accompanying CSV separately retains Table 4 payload-sensitivity values for reference; the Table 4 group is not plotted in this panel.

Table 4, epsilon = 0.2 (CSV reference only):
0.1 bpp = 46.85%; 0.2 bpp = 42.54%; 0.4 bpp = 35.62%.

Table 11, 0.4 bpp (shown in the revised panel):
epsilon = 0.1: 33.41%; epsilon = 0.2: 35.62%; epsilon = 0.3: 32.88%.

This is a corrected visualization of existing published table entries, not a new measurement or reconstruction from recovered plotting records. The original Figure 8(a) is unchanged.

## Evidence boundary

The released package does not contain the original complete PPO/DQN/U-Net/SRM-SRNet experimental pipeline, original trained weights, original 5,000-image split, five-seed results, or original Figure 8(b) run-level data.

Neither the corrected C demonstration nor the independent pilot validates the published steganalysis results. Published numerical tables are retained as transcriptions with explicit provenance.

## Data and integrity

Third-party benchmark images are not redistributed. Use the portable dataset manifest to identify and obtain authorized source images.

Refer to:
- README.md
- independent_reconstruction/pilot_40/README.md
- independent_reconstruction/pilot_40/evidence/METHODS_AND_REPRODUCIBILITY.md
- SHA256SUMS_RELEASE.txt

Related publication:
https://doi.org/10.1016/j.image.2026.117652