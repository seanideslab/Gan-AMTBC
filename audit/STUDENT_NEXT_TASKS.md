# GAN-PPO-AMBTC｜下一階段學生工作單：已刊登圖表一致性核查

**指定資料：** 正式刊登 PDF `[2]Security-AMBTC-Compressed 0726.pdf`、新版 ZIP `Gan-AMTBC_figure_audit_v2.zip` 的 `audit/`、先前 `FORMULA_AND_FIGURE_AUDIT.md`。**不必再跑 C demo，不要求重訓原始模型。**

**目標：** 找出正式論文中圖、表、內文、公式之間的數值與定義不一致，製成「原文位置—問題—證據—處理建議」清單，交老師決定後續更正。只處理可追溯的出版紀錄；不把同一數字在不同位置重複出現視為獨立實驗驗證。

## 1. 優先核查（先做完再擴充）

- **Fig. 8(b)／Tables 4、10、11／摘要（PDF pp. 1, 9, 12–14）：** 逐格核對 ε = 0.2 的三種 bpp；另核對 ε = 0.1／0.3 在 0.4 bpp 與 Table 11。正式 PDF Fig. 8(b) 最右橘色標籤為 **11.90%**（勿沿用舊報告的 11.90%）。使用 ZIP 中 `audit/check_fig8b_publication.py` 輸出比對表。**不得用 Table 4 數值直接替換 Fig. 8(b) 全部九根柱子。**
- **Fig. 6（p. 10）：** 圖說宣稱 Proposed 的 P_E 最高，但繪圖中的藍色柱最短；另外檢查重複圖例、隨機猜測基準線位置、y 軸刻度。註明需圖形原始數據才能重畫。
- **Fig. 7（p. 13）／Table 2（p. 3）／Fig. 8(a)（p. 14）：** 200 epochs 與 Fig. 7 橫軸到 500 的差異；Fig. 7(c) 紅線高於 44 dB 與表列 40.35 dB 的指標／條件差異；圖例重複及「80／120 epochs」是否衡量不同收斂標準。不要自行改動曲線。
- **Fig. 5（p. 9）／Tables 3a、3b、4（pp. 3, 8–9）：** 核查圖例對應，特別是 HILL 曲線與 Table 3b（38.07 dB、0.974）；核查 PSNR／SSIM 跨 bpp 的平線是否有逐負載數據支持。Fig. 5(c) 核對 Table 4 之三種負載。
- **§4.4 Double-Tanh（p. 6）：** 並列正式公式與 C utility，註明 C utility 未進入 demo 推論流程；在找不到原始 Python 訓練碼的情況下，**不自行選定原研究實際使用的公式**。

## 2. 其餘完整性快查

逐一檢查 **Figs. 1–4、Tables 1–2、3a–3b、5–9** 的圖號／表號、caption、單位、軸、圖例、正文引用及數值是否對應。Fig. 4 特別查明彩色示意影像與灰階 benchmark 的關係；Fig. 3 需註明 action-usage 統計所對應的 payload／測試集（若原文未指明，記「未交代」）。

## 3. 交付物（只交一個 `PAPER_FIGURE_AUDIT_FINAL/`）

1. `FIGURE_TABLE_MATRIX.md`：每張圖／每張表一列，欄位「PDF 頁碼｜原始標籤／數字｜正文／表格對應｜問題｜證據位置｜建議處理｜狀態」。可沿用新版 ZIP 預填表。
2. `PROPOSED_CORRECTION_LIST.md`（最多 2 頁）：只挑可明確定位的錯誤，列「原文／建議修訂／依據」；**沒有原始資料的圖，只寫待取得來源／需請編輯指示，不猜測修正數值**。
3. `EVIDENCE_INDEX.md`：列正式 PDF 頁碼、所用 CSV／程式／截圖來源及 SHA-256。圖表截圖留在工作資料夾供老師核對；公開 GitHub 可只保留頁碼與轉錄，勿未經確認上傳整篇出版 PDF。

**狀態只用：** `PRINT_CONSISTENT_ONLY`（刊本內互相一致，不代表實測）、`PRINT_CONFLICT`、`PRESENTATION_ERROR`、`SOURCE_MISSING`、`NEEDS_AUTHOR_DECISION`。

**禁止：** 將 C demo 結果替換論文結果、補造五次實驗或原始曲線、只為使趨勢一致而改圖、覆蓋舊版 GitHub 或宣稱已完成科學重現。你只需做出版層級的查核，老師負責正式更正與回覆期刊。
