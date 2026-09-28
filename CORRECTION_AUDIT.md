# GAN-PPO-AMBTC 公開資料包技術審核與修復紀錄

**基準**：使用者提供的 `Gan-AMTBC-main.zip`、正式發表 PDF：*Signal Processing: Image Communication* **148 (2026) 117652**, DOI **10.1016/j.image.2026.117652**。本報告區分「原始公開程式」、「正式刊登論文」、「新修復的獨立示範」，沒有把任何新示範測試數字冒充為原始論文實驗。

## 1. 實際檢出

| 問題 | 原始證據 | 影響 | 修復方式／限制 |
|---|---|---|---|
| 論文數字以常數輸出 | `src/export_ablation.c` 用 `fprintf` 寫入 Table 4／10 的數值 | 不能視作實驗結果的程式重現 | 移除偽實驗 exporter；已刊數據移至 `paper_reported/` 並註明「刊登數據轉錄、未獨立驗證」。 |
| 假訓練曲線 | `src/train_stub.c` 透過線性公式寫 `training_log.csv` | 無法證明圖 7／8(a) 收斂性 | 移除該程式和訓練日誌；必須取得原始 epoch logs。 |
| 資料與權重 | `Data/splits/train.txt` 與 `val.txt` 空白；`test.txt` 僅一筆失效的本機路徑；`weight/policy_smoke.txt` 為未訓練 toy | 無法重現 5000 影像與五個 seeds | 移除虛假 split 檔；提供建立「新實驗」split 的腳本；列出缺失清單。 |
| 原本 0.2／0.4 結果相同 | 原始 C inference 各區塊獨立決策，沒有實際全圖預算投影；在 toy 64x64 結果都 1024 bits = 0.25 bpp | 圖像與負載未依目標變化 | 新 C **示範用** budget projection 達到可表示的接近整數 bit；加入唯一 bitmap 位置與回讀測試。不是原論文 PPO。 |
| BER 不實測 | `evaluate.c` 直接向 CSV 寫 `bit_errors=0` | 將未驗證的 0 誤認為真實測量 | 改成實際比對 in-memory AMBTC bitmap 的位元，欄名 `verified_bitmap_bit_errors`；**不**宣稱對 JPEG/AWGN 有效。 |
| 形式與程式不一致 | Published §4.4 uses tanh difference; 原 C utility 是 `0.5*(tanh(...)+tanh(...))`、`alpha=beta=8, tau=.15` | 論文宣稱 α=10, β=5, τ=.5；code 不支持此超參數及訓練流程 | 提供有中心校正、範圍[-1,1]的新 utility 作候選參考；**無法推定發表實驗實際使用何式**。 |
| Figure 8(b) 與表不符 | 發表 PDF 第14頁、Table 4 / Table 11 | 直接衝突，且影響安全性主張呈現 | `reproduction/figure8_audit.py` 精確核對；需要原始 ε／bpp logs 後才能製作正式修正版。 |
| PDF 與 GitHub 連結不吻合 | Published data availability 指向 GitHub archive，但完整原始 pipeline 沒有隨 ZIP 提供 | 目前的開源可重現性陳述過度寬泛 | README 揭露範圍，要求增補原始實驗資產與 journal correction。 |

## 2. 形式精確計算

發表版 §4.4 所印（α=10, β=5, τ=0.5）：

`psi_wrong(x) = tanh(alpha*(x-tau)) - tanh(beta*(x+tau))`

`psi_wrong(0) = tanh(-5) - tanh(2.5) ≈ -1.98652`；對原點具有重大偏移。

原始 C demo 所用 utility：

`psi_C(x)=0.5*[tanh(alpha*(x-tau)) + tanh(beta*(x+tau))]`

**僅在 alpha=beta 等對稱條件下保證 psi_C(0)=0**。原 C 預設正是 alpha=beta=8，但這與正式 PDF 所列 alpha=10,beta=5 不相同。若僅把論文減號改加號並保持不等斜率，`psi_C(0)≈-0.006648`，依然不是精確零。

本修復版額外提供可對不等斜率維持原點為零、值域在 [-1,1] 的**獨立參考候選**：令 `f(x)=tanh(alpha*(x-tau))+tanh(beta*(x+tau))`，`c=f(0)`，則

`psi(x)=(f(x)-c)/(2-c)` 當 `f(x)>=c`，否則 `psi(x)=(f(x)-c)/(2+c)`。

這是新提出的數學修復候選，不得直接宣稱為已刊實驗實作。`double_tanh()` 在 C demo 只是工具函式，並未構成 U-Net 或真正可微訓練器。

## 3. Figure 8(b) 的完整衝突

| payload | Figure 8(b) ε=.2 | Table 4 full model | 差異（表－圖） |
|---|---:|---:|---:|
| 0.1 bpp | 35.62% | 46.85% | +11.23 pp |
| 0.2 bpp | 28.50% | 42.54% | +14.04 pp |
| 0.4 bpp | 15.80% | 35.62% | +19.82 pp |

Table 11 在 ε=.1/.2/.3、**0.4 bpp** 分別列 33.41%／35.62%／32.88%；這一組數值卻出現在 Figure 8(b) 的**0.1 bpp** 群組。最少表示 group/axis label 或繪圖來源不符。不可擅自把 0.4 bpp 的 Table 11 三個值搬到 0.4 群組再補造 0.1、0.2 數值。圖 8(a) 的訓練曲線也沒有原始 epoch log 支援。

## 4. 研究重現性的明確邊界

已修復：toy C 的 AMBTC 編解碼、可行負載、不同負載的不同輸出、從 sidecar 實際抽取、示範用 PSNR/global SSIM；提供直接推論**外部真實 TorchScript 權重**的評估 adapter，能統計 PFA、PMD、PE、windowed SSIM、PSNR；提供只有在原始五個 seed 紀錄存在時才運作的結果彙總。

**尚未修復／無法憑空取得**：原始五次訓練與 5000-image holdout 名單、真正 PPO/DQN/U-Net 權重、SRM/maxSRMd2 feature extractor、SRNet/ERANet/SiaStegNet checkpoint 與設定、原始 cover/stego pairs、所有 ablation seed logs、Figures 7/8 曲線來源、原始性能測試 log。這些才是核實刊登數據的必要證據。

C 的 `.pgm` 是解碼的圖片預覽；實際抽取依賴輸出的 `.ambtc` triplets 與 `.map` side information。不能因此宣稱任意 PGM/JPEG 傳輸後亦可抽回原 bitstream。

## 5. 出版處理建議

本論文已刊登，應主動聯繫期刊編輯，附件可提供本清查、原始檔與更新檔差異、真實原始數據（如能取回）及必要 correction proposal。請期刊決定正式 corrigendum／其他處置。先更新 GitHub README 和 release note 揭露現狀，不應僅覆蓋檔案讓研究紀錄消失。見 `EDITOR_CORRECTION_REQUEST.md`。

另請核對刊登 PDF declaration 使用 `Shou-En Investment Co., Ltd.`，與先前聲明的 `En-Shou Investment Co., Ltd.` 相反，屬另一項待與 journal 核實的名稱誤植。
