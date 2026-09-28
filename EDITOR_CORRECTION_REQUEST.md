# Editorial notification draft — send after confirming factual attachments

**Subject:** Request for editorial assessment of reproducibility-package and figure/equation discrepancies — DOI 10.1016/j.image.2026.117652

Dear Editor,

I am the sole author of the article “Security-Aware Payload Control and Residual Suppression for Data Hiding in AMBTC-Compressed Images,” published in *Signal Processing: Image Communication*, 148 (2026), 117652 (DOI: 10.1016/j.image.2026.117652).

During a post-publication audit of the publicly linked GitHub research package, I identified issues that I would like to disclose promptly and correct transparently:

1. The released C package is a demonstration scaffold rather than the original PPO/DQN/U-Net training and full steganalysis evaluation pipeline. Its previous result-export utility transcribed reported table values instead of computing them from raw experiment records. I am replacing that functionality with explicitly labeled publication transcriptions and scripts that require genuine run-level evidence.
2. Section 4.4 prints a Double-Tanh expression with a subtraction that is inconsistent with the released C utility and is nonzero at the origin. The exact mathematical correction must be established against the original experimental implementation and logs before the article text is amended.
3. Figure 8(b) has a numerical discrepancy: for epsilon = 0.2, its 0.1/0.2/0.4 bpp labels are 35.62%/28.50%/15.80%, whereas Table 4 reports 46.85%/42.54%/35.62% for the full model. Table 11 also gives 35.62% at epsilon = 0.2 and 0.4 bpp. I am verifying the original plot data before proposing a corrected figure.

I am auditing the original experiment records and am preparing a versioned repository update that explicitly distinguishes demonstration outputs, published tabulations, and independently reproduced results. The attached technical audit lists what is and is not currently verifiable from the released files. I will provide any original model checkpoints, run-level results, and revised figure/equation files as they are located and verified; I will not infer or synthesize missing experimental outcomes.

Could you advise the appropriate formal mechanism, including whether a corrigendum and/or an editorial review of the underlying evidence is necessary? I would be grateful for instructions on the evidence and file format you would like me to provide.

I have also noticed that the competing-interest statement prints “Shou-En Investment Co., Ltd.”; please advise whether the intended name “En-Shou Investment Co., Ltd.” can be corrected in the same process.

Thank you for your assistance in maintaining an accurate scientific record.

Sincerely,
Shang-En Tsai
Corresponding author
sean@mail.cjcu.edu.tw
