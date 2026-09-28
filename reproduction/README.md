# Reproduction status and instructions

## What these scripts really do
- `figure8_audit.py` audits *published figures/tables*; it does not calculate model outputs.
- `aggregate_runs.py` requires 5 independent real experiment rows for each (variant, detector, bpp) and reconstructs detection error from observed confusion counts. It refuses absent raw data and duplicate seeds.
- `score_torchscript.py` calculates actual confusion counts, image PSNR, windowed SSIM on user-supplied paired images and a REAL trained, TRUSTED TorchScript detector checkpoint. It does not supply SRM/maxSRMd2/SRNet/ERANet/SiaStegNet weights. If SRM features are required, they must be integrated inside a verified checkpoint or provided by a separate validated feature extractor.
- `new_split.py` builds a NEW split from legally obtained full dataset inventories. It cannot reconstruct the historical split from an empty folder.
- The C demonstration does not train PPO, DQN or U-Net. It is not the scientific model from the article.

## How to run the audit
```
python3 reproduction/figure8_audit.py
python3 reproduction/aggregate_runs.py reproduction/raw_runs_template.csv results/verified.csv
```
The second command **should fail** until real experimental records are entered. This is intentional.

## Genuine detector evaluation (external checkpoint required)
```
python3 reproduction/score_torchscript.py \
  --model /path/to/real_trained_detector.pt \
  --pairs /path/to/pairs.csv \
  --detector SRNet --variant full --bpp 0.4 --seed 0 \
  --out /path/to/raw_run_0.csv
```
`pairs.csv`: `image_id,cover_path,stego_path`, with one cover and one stego of same resolution per ID. For detector comparisons, retrain/validate properly without leaking any held-out test images. Checkpoint class output must be calibrated as class 1 = stego. Use real **independent** seeds and actual ground truth. Do not relabel a toy classifier as SRNet, ERANet, or SiaStegNet.

## Evidence needed to reproduce publication values
1. Actual original 5000-image BOSSbase split IDs, all training/validation IDs, preprocessing scripts and hashes.
2. Trained PPO actor, DQN, U-Net generator and SRM-SRNet checkpoint per seed; scripts that produced them.
3. True stego bitstream and extraction algorithm, including capacity side information and any error correction.
4. SRM/maxSRMd2 feature extractor version, steganalyzer training scripts, external models for ERANet and SiaStegNet, detector evaluation scripts and test predictions.
5. Raw five-seed PSNR/SSIM/PE confusion counts and logs for Tables 4/10/11, as well as the data generating Figures 7/8.
6. Hardware benchmark logs and any declared INT8 model. No such files were included in the uploaded ZIP.

The source publication reports several quantities not established by this package. No new numerical result should be substituted into the paper without rerunning those experiments or locating and verifying their original records.
