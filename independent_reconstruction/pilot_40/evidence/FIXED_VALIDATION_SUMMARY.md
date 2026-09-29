# FIXED_VALIDATION_SUMMARY

**NEW_INDEPENDENT_RECONSTRUCTION / SMOKE_ONLY / FIXED_VALIDATION**

**結論：兩個 payload 的固定 validation MSE 均逐 epoch 下降，補償平均 MSE 低於 baseline；best＝epoch 3。此次小型補測條件通過，停止於指定 3 epochs，是否擴大仍由老師決定。**

沿用原 manifest（train 20／val 10／test 10）、40 張原始 BOSSbase 影像與 seed=42。從新隨機初始化開始：base=50、4,962,229 參數、64×64 整圖 resize、batch=2、targets=0.2／0.4、smoke；未載入舊權重。原成果已備份且核對未改變。

| Epoch | Val 0.2 baseline／corrected MSE | Val 0.4 baseline／corrected MSE | 固定條件平均 corrected MSE | Best? |
|---|---|---|---:|---|
| 1 | 0.0045662306／0.0045390395 | 0.0050593813／0.0050272760 | 0.0047831577 |  |
| 2 | 0.0045662306／0.0044911824 | 0.0050593813／0.0049895557 | 0.0047403690 |  |
| 3 | 0.0045662306／0.0044200402 | 0.0050593813／0.0049094832 | 0.0046647617 | 是 |

每個 payload 每個 epoch 均為同 10 張 val；固定 epoch=0、shuffle=False、batch=2。逐張秘密訊息、load、bitmap 雜湊跨 epoch 一致；完整摘要與 60 筆 val 逐張 MSE 已保存。原混合 validation 另保留，未用於選模。最低 fixed_score 選定 best 並鎖定 SHA-256 後，holdout 各跑一次。

| Best holdout | 張數 | Achieved bpp | Baseline → compensated MSE | Baseline → compensated PSNR (dB) | 改善張數 | Bit errors |
|---|---:|---:|---|---|---:|---:|
| 0.2 bpp | 10 | 0.199951171875 | 0.005554089 → 0.005395842 | 23.878833 → 23.973766 | 9／10 | 0 |
| 0.4 bpp | 10 | 0.399902343750 | 0.005971218 → 0.005804508 | 23.462654 → 23.568102 | 9／10 | 0 |

MSE 與 PSNR 全部參考同一 AMBTC cover、像素 [0,1]。逐張直接算 mean((重建−cover)²)，PSNR＝−10 log10(MSE)，表內各自對 10 張取算術平均；無 vs_raw 混比。holdout MSE 直接於原評估 forward 保存，未另跑 test 推論。

環境：Intel Core 7 150U／Intel Graphics，CPU；Python 3.12.14、PyTorch 2.8.0+cpu、CUDA 不可用。v6 測試經既有 Windows 暫存 fixture 相容處理 5／5 通過。run_epoch、make_pair、loss、模型、資料切分保持原樣；新加固定驗證不影響訓練 RNG。第 3 epoch 模型張量與上輪相同 seed 的重跑結果完全一致，是可重現性核對，並非載入舊權重。

已保存三個 epoch 權重、best、latest、manifest 原始副本／雜湊、程式差異、環境與命令、逐張資料。bitmap 回讀零錯誤不等於一般圖片檔端到端解碼；此輪未訓練 PPO／DQN／SRNet，也未估計 P_E、修改已發表表格。本次同資料重跑不增加獨立樣本數。

Best epoch：3 / checkpoint SHA-256：`dcbb6440dd1db5f70240c48013e6d3feed7faaf693a4e122276eb9231a944639` / Holdout 0.2: bpp=0.199951171875, MSE=0.005554089→0.005395842, PSNR=23.878833→23.973766 dB, 改善=9/10, bit errors=0；0.4: bpp=0.399902343750, MSE=0.005971218→0.005804508, PSNR=23.462654→23.568102 dB, 改善=9/10, bit errors=0
