# 2026-09-29 parameter-note integration: scope and provenance

Source: a one-page Chinese lab summary supplied by the author. SHA-256: `5c3ddc86452bf54a72836a6da1c1c488bd3af7ec457914214a329258626b1d1d`. Its creation date, relation to other revisions and whether it represents the final experiment are **not established**. This version retains the raw original separately under the author's custody; it is not added to the public GitHub package.

## Direct data extracted from the note
- PPO: two hidden layers, 256 neurons each; approximate count 0.12M; orthogonal initialization with gain sqrt(2), actor output gain .01.
- DQN: two hidden layers of 64 neurons, four outputs; Kaiming initialization, unspecified small security-preferring output bias.
- U-Net: four encoder/decoder stages; *estimated* encoder channels 32/64/128/256; approximate reported 4.87M; Kaiming initialization and suggested small last-layer gain.
- SRM front end: 30 frozen 5x5 kernels, shape [30,1,5,5]; the actual filter coefficients are not included.
- State (QLD, block variance), actions (1,2,4,8), clip .2, gamma .99, GAE .95, budget .1; DQN epsilon schedule, soft target updates and buffer settings.
- Training: Adam, batch 16, epochs 200, discriminator/generator learning-rate ratio 4, Double-Tanh alpha 10/beta 5/tau .5.

## Explicit non-findings
The source has no .pt/.pth checkpoint, no actual learned tensor, no Python module, no BOSSbase IDs or image data, no SRM coefficient array, no five independent seed logs and no chart source CSV. Reconstructed classes are new demonstrations of shape and parameter bookkeeping, not the original implementation.

## Conflicts that must remain visible
- Old `configs/default.cfg`: batch 8. The archived note and final paper Table 7(b): batch 16. A distinct PyTorch recovery config is added; the C-demo file remains unchanged.
- DQN reward control: archived note says lambda1/lambda3; paper describes lambda1 and a joint lambda2/lambda3 action. No exact mapping is implemented.
- PPO paper description uses a shared two-layer backbone, but approximate 0.12M cannot identify its exact topology; neither alternative in this archive is claimed as original.
- U-Net channel schedule is explicitly estimated and insufficient to reconstruct the reported 4.87M network.
- The Double-Tanh parameters are corroborated, but the training-time equation is unknown and the published expression remains mathematically discrepant. The centered formula is a **new candidate only**.
