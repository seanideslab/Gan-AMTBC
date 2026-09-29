# MVR_RECHECK — 修復版功能實測摘要

執行：2026-09-28，台灣時間（UTC+08:00）。輸入為指定 `Gan-AMTBC_repaired_transparency_v1.zip`，非舊 commit；SHA-256 與環境見 `ENVIRONMENT.json`。本次只操作新解壓副本，未修改原始 ZIP、GitHub 或既有 MVR_48h。

**實測完成：** 原附 lena_like_64 加三張明確標為合成的 P5 灰階測試圖，均 64×64，分別執行 0.1、0.2、0.4 bpp，共 12 組。各組 embedded bits 為 410、819、1638；actual bpp 為 0.10009765625、0.199951171875、0.39990234375。獨立執行 extractor 回讀全部 0 bit errors，payload/recovered bytes 及 SHA-256 全相同。原附範例三種負載 PGM hashes 互異。PGM、AMBTC、map、payload、recovered、逐次 log 與 hashes 均保存。

原附範例 PSNR 分別為 32.9217、31.6995、29.9147 dB；global SSIM 為 0.993288、0.991100、0.986593。CSV 全部標記 `DEMO_NOT_PAPER`，由實際輸出重新計算並核對 C 列印值；global SSIM 使用全圖樣本變異/共變異，並非 windowed SSIM。三張額外圖是可重建功能 fixtures，不是自然影像 benchmark。policy_smoke.txt 僅作未訓練 toy 設定。回讀依賴 .ambtc 與 .map，未宣稱僅從 PGM 可恢復 payload。

**完整測試未通過：** 初始無 make；補齊 GNU make 4.4.1 與 BusyBox shell 後，`make clean`、`make` 成功。`make test` 在 extractor 啟動遭 Windows 應用程式控制封鎖（4551）；另一個 math executable 同樣被封鎖。Python unittest 曾因 MSYS Python DLL 被封鎖及 bundled Python tempfile 權限問題而失敗。未停用任何保護措施，所有失敗均保存。這些環境失敗不能算測試通過，也不能直接歸因為演算法缺陷。`figure8_audit.py` 成功。

**圖表與公式：** Double-Tanh 是獨立中心校正 utility，未被 demo 嵌入流程呼叫；不能推定原 PyTorch 訓練公式。ZIP 轉錄顯示 Figure 8(b) epsilon=.2 對 Table 4 的 PE 差為 +11.23、+14.04、+19.82 pp（表－圖）。這僅是轉錄比對；尚未取得刊登 PDF 與上次 FORMULA_AND_FIGURE_AUDIT.md，Figures 5–7、PDF 逐格與正文/epoch 核查未完成。詳見 FIGURE_EQUATION_AUDIT.md。

**仍缺：** 原 PPO/DQN/U-Net 模型與設定、原始 splits/5000-image holdout、五個 seeds 的 checkpoints、detector/feature extractor、cover/stego pairs、ablation/epoch/raw logs。無法判定刊登數字哪個正確；沒有重現論文性能、五個 seeds 或 steganalysis。待提供刊登 PDF 與舊核查文件後，才能完成 B 項核查。
