# Narrow proposed text amendments for editorial consideration

**This document does not amend the publisher PDF.** Changes requiring model evidence remain flagged.

## Bibliography replacements with verified identities

- [36] G. Xie, J. Ren, S. Marshall, H. Zhao, R. Li, R. Chen, “Self-attention enhanced deep residual network for spatial image steganalysis,” *Digital Signal Processing*, vol. 139, article 104063, 2023. DOI: 10.1016/j.dsp.2023.104063.
- [37] W. You, H. Zhang, X. Zhao, “A Siamese CNN for Image Steganalysis,” *IEEE Transactions on Information Forensics and Security*, vol. 16, pp. 291–306, 2021. DOI: 10.1109/TIFS.2020.3013204.
- [28] V. Holub, J. Fridrich, T. Denemark, “Universal distortion function for steganography in an arbitrary domain,” *EURASIP Journal on Information Security*, vol. 2014, article 1, 2014. DOI: 10.1186/1687-417X-2014-1.
- [29] V. Holub, J. Fridrich, “Designing steganographic distortion using directional filters,” IEEE WIFS, pp. 234–239, 2012. DOI: 10.1109/WIFS.2012.6412655. Remove the appended label implying that this entry itself is the 2014 full UNIWARD reference. Recheck in-text S-UNIWARD cites for [28].
- [39] Current arXiv reference belongs to another work. Keep unresolved and seek editorial agreement to delete the unsupported MORSE-specific prose and reference if the authentic source is not recoverable. Renumber only as journal production directs.

## Figure 8(b) factual description (not replacement experimental numbers)

The published figure labels for epsilon 0.2 are 35.62%, 28.50% and 15.80% at 0.1, 0.2 and 0.4 bpp, respectively. The full-model row in Table 4 gives 46.85%, 42.54% and 35.62%. The 0.4 bpp Table 11 epsilon=0.2 value is 35.62%. The source records needed to choose corrected numerical values are not present in the released materials. Figure 8(b)'s epsilon=0.3 / 0.4 bpp orange label reads **11.90%** in the official PDF (correcting the v2 audit transcription).

## Section 4.4 candidate clarification, pending verification

“The printed subtraction expression does not have the stated bounded ternary behavior. The released C utility implements a bounded centered-sum candidate and is not used by the C demonstration embedding routine. The original training implementation has not been identified in the released package; therefore the candidate expression cannot presently be certified as the formula used in the published experiments.”

Do not assert that replacing `−` with `+` alone exactly fixes the origin for alpha=10, beta=5, tau=.5: a direct half-sum gives approximately -0.006647 there.

## GitHub code scope

Software release should be described as a corrected **standalone C demonstration and post-publication audit**, not full PPO/DQN/U-Net implementation, and numerical files copied from publication must remain clearly labeled as read-only transcriptions.
