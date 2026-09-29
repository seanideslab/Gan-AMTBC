# Published figure/table cross-check register — working copy

Article: S.-E. Tsai, *Signal Processing: Image Communication* 148 (2026) 117652, DOI: 10.1016/j.image.2026.117652. Reference: published PDF `[2]Security-AMBTC-Compressed 0726.pdf`; SHA-256 in `audit/SOURCE_MANIFEST.md`. PDF page numbers below are **printed article pages**, not Editorial Manager submission pages.

**Scope:** This is a comparison of the published presentation against itself, supplemented by a corrected C **demonstration** test. It does not independently authenticate the reported experimental measurements. The original raw data, five-seed logs, checkpoints and detector were not found in the surviving repository. The table values below are publication transcriptions, not replacement results.

| Object | Published page | Specific audit point / published reference | Preliminary status | Evidence required / next step |
|---|---:|---|---|---|
| Fig. 1 | 5 | PPO/DQN/U-Net workflow, action set {1,2,4,8}; compare §4 | SOURCE_MISSING | Check arrows, symbol definitions and caption only; no model weights to validate diagram. |
| Fig. 2 | 6 | Embedding/training stages, SRM–SRNet path | SOURCE_MISSING | Confirm caption/flow against §4.2–4.5. |
| Fig. 3 | 8 | Learned policy map and action-usage chart | NEEDS_AUTHOR_DECISION | Identify the target bpp and image population represented by plotted action frequencies; do not assume 0.4 bpp. |
| Fig. 4 | 9 | Three cover/stego/residual rows 0.1/0.2/0.4 bpp; images appear RGB although benchmark is described as grayscale | NEEDS_AUTHOR_DECISION | Clarify image provenance, whether qualitative visualization uses different source, and individual PSNR/SSIM source. |
| Fig. 5(a,b) | 9 | Published GAN PSNR and SSIM traces are flat across three bpp settings; Table 3a reports one overall 40.35 dB / 0.991 pair | SOURCE_MISSING | Locate per-bpp source series, or explicitly state the scope of Table 3a. Do not create numeric series from a single table cell. |
| Fig. 5(a,b) | 9 | Orange HILL line appears at about 36 dB / 0.981, while Table 3b lists HILL 38.07 dB / 0.974 at 0.4 bpp | PRINT_CONFLICT | Review series-to-legend mapping, possible mismatch with HPDH-MI; original chart data needed. Visual estimates are not corrected values. |
| Fig. 5(c) | 9 | P_E trends vs Table 4 | PRINT_CONSISTENT_ONLY | Confirm series mapping and three printed target rates without treating chart image as raw data. |
| Fig. 6 | 10 | Caption says GAN-PPO-AMBTC highest P_E, but visually blue Proposed bars are lowest; duplicated legend entries and misdrawn 50% random-guess line; y ticks duplicate 20 | PRESENTATION_ERROR | Find detector-wise source data; otherwise report diagram-caption mismatch, not made-up revised bars. |
| Fig. 7(a,b,c) | 13 | Epoch axis to 500 vs Table 2 200; duplicated/misassigned legend; red PSNR in (c) >44 dB vs Table 3a/10/11 40.35 dB | PRINT_CONFLICT | Check if plotted metric, run phase or image set differs. No axis relabeling or hand-redraw without logs. |
| Fig. 8(a) | 14 | ε=0.2 convergence at ~80 epochs vs Fig. 7 ~120-epoch system stabilization | NEEDS_AUTHOR_DECISION | Identify whether different indicators/criteria are intended; 200-epoch axis here vs Fig. 7 500. |
| Fig. 8(b) | 14 | ε=.2 at 0.1/0.2/0.4 bpp = 35.62/28.50/15.80%, but Table 4 full model = 46.85/42.54/35.62% | PRINT_CONFLICT | Check all nine cells in `FIG8B_PUBLICATION_CROSSCHECK.csv`; verify final orange 0.4-bpp label 11.90%, not 11.90%. Replacement data cannot be inferred from tables. |
| Table 1 | 2 | Threshold-classification terminology | PRINT_CONSISTENT_ONLY | Confirm caption/labels/threshold symbol consistency. |
| Table 2 | 3 | Training schedule 200 epochs, clip ε=.2, metrics | PRINT_CONFLICT | Cross-reference Fig. 7 epoch labels; check other values against text. |
| Table 3a | 3 | Proposed 40.35 dB / 0.991, adaptive payload description | PRINT_CONSISTENT_ONLY | Check correspondence with Tables 10/11 and per-payload interpretation in Fig. 5. |
| Table 3b | 8 | HILL 38.07 dB / 0.974, S-UNIWARD 38.00 dB / 0.971 at 0.4 bpp | PRINT_CONFLICT | Cross-check Fig. 5(a,b) HILL legend. |
| Table 4 | 9 | Proposed 46.85/42.54/35.62% at 0.1/0.2/0.4 bpp | PRINT_CONFLICT | Agrees with abstract; contradicts Fig. 8(b) ε=.2 at every bpp; no original run data. |
| Table 5 | 9 | ERANet/SiaStegNet metrics at 0.4 bpp | SOURCE_MISSING | Verify labels and cross-text only; no model evaluation evidence. |
| Table 6 | 10 | AWGN/JPEG and BER | SOURCE_MISSING | Check units, σ² vs σ and article text; no raw BER traces. |
| Table 7a/7b | 10–11 | Inference/time setting / training or convergence settings | SOURCE_MISSING | Check hardware names, FPS arithmetic, 200-epoch statement vs Fig. 7. |
| Table 8 | 11 | MRI comparisons | SOURCE_MISSING | Check caption, dataset origin, sample count, PSNR/SSIM/P_E narrative. |
| Table 9 | 11–12 | Failure-mode analysis | SOURCE_MISSING | Check numbers/percentages against text. |
| Table 10 | 12 | Full model 40.35 dB, 0.991, P_E 35.62% at 0.4 bpp | PRINT_CONSISTENT_ONLY | Matches Table 11 ε=.2 / abstract for 0.4 bpp, but not independent experimental evidence. |
| Table 11 | 13 | 0.4-bpp ε=.1/.2/.3 P_E in interpretation text: 33.41/35.62/32.88% | PRINT_CONFLICT | Values appear in Fig. 8(b) under **0.1 bpp** rather than 0.4 bpp; no basis to select corrected figure cells. |
| §4.4 equation | 6 | Published tanh difference vs available C centered sum; C function not used by demo | PRINT_CONFLICT | Original PyTorch implementation unavailable; do not assert original training used repaired C formula. |

**Suggested disposition codes:** `PRINT_CONSISTENT_ONLY` = agrees at publication print level; `PRINT_CONFLICT` = article displays incompatible labels/values for nominally matching setting; `PRESENTATION_ERROR` = axes/caption/legend mismatch; `SOURCE_MISSING` = source data required; `NEEDS_AUTHOR_DECISION` = ambiguity needing method clarification. Multiple codes may apply to the same item.

**Review rule:** Do not change published numerical claims to force agreement, and do not publish a reconstructed Figure 6/7/8(b) without authentic source data or transparently identify it as a newly created illustration. The journal decides the formal correction mechanism based on documented scope and evidence.
