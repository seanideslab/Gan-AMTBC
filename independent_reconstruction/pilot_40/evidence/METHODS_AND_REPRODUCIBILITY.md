# 固定驗證：方法、檔案與重現說明

標示：NEW_INDEPENDENT_RECONSTRUCTION / SMOKE_ONLY / FIXED_VALIDATION。

## 最小程式修改

`v6_fixedval.patch` 與 `source/new_training/` 提供實際執行版本。`train_generator.py` 原有 run_epoch()、make_pair() 以 AST 比對確認不變；models.py、ambtc.py、data.py 逐 byte 不變，loss／optimizer／gradient accumulation／訓練資料 loader 未改。

新增固定 epoch=0 的 0.2／0.4 獨立 validation，將兩者 corrected_mse 算術平均作 fixed_score，嚴格小於既有 best 才更新（同分保留較早 epoch）。保留原混合 validation，額外寫 fixed_val、fixed_score、設定雜湊；另存各 epoch 完整 checkpoint，從最佳 epoch 檔直接複製 best，並記錄 SHA-256。額外的 validation loader 迭代前後保存／恢復 CPU RNG，避免其 seed 消耗改變訓練 RNG 進程；本輪 CPU、模型無另增隨機層。

`fixed_validation_config.json` 記錄 20 個 image×payload 設定：影像 SHA-256、固定 batch 索引、pair_seed、embedding key、各 block 的完整 loads，以及實際 secret bytes、stego bitmap 的 SHA-256。每 epoch 重新產生並檢查同一總雜湊；每個 pair_seed 皆等於固定 batch index（相當於 epoch*1,000,000+batch 且 epoch=0），每張訊息的 PRNG seed 延用 v6 sha256(image_hash:pair_seed:target) 算式。

v6 的 run_epoch bit_errors 欄位原本初始化為 0，但 make_pair 會逐張實際 extract 並在不一致時直接拋出異常；另以 `fixed_validation_per_image.csv` 的逐張實際抽取差異再次核對 val。基準、秘密與 loads 固定，模型輸出可以隨 epoch 改變。

`evaluate_new.py` 僅在原有一次 forward 中追加 baseline_mse_vs_ambtc、corrected_mse_vs_ambtc 與 provenance，並擴充 summary。選模之前沒有執行本輪 holdout；selection_locked_before_holdout.json 的 UTC 時間早於 execution_logs/commands.json 中兩個 holdout 起始時間。每個 payload 恰好一個成功 evaluation command，之後只讀 CSV 計算摘要，不重跑 test。

## 逐張數值

- `fixed_validation_per_image.csv`：60 行＝3 epochs×2 payloads×10 val 圖；使用各 epoch 權重及相同 make_pair 規則，與 training_log 彙總核對，float32 每圖／整 batch reduction 順序差容許 2e-9 MSE。
- `holdout_best_0p2.csv`、`holdout_best_0p4.csv`：各 10 行，包含原始指標以及直接逐張 MSE。paired 指每張圖使用同一 cover／訊息／loads 比較 baseline 與 compensated。
- PSNR 為 peak=1 的 −10 log10(MSE)。摘要中的平均 PSNR 是逐張 PSNR 的平均；不可將其等同於平均 MSE 的 PSNR。兩份 CSV 所有 vs_ambtc 欄位均以相同 cover 為參考。
- `verification_report.json` 包含一致性、best、雜湊、改善張數、逐 payload 彙總。模型張量与上輪 epoch 3 一致，是同 seed／同資料／同演算法的可重現性，而非新資料的獨立驗證；checkpoint 檔案雜湊不同，因新增 metadata 與 validation 記錄。

## 保留與路徑

`preservation_record.json` 記錄上輪完整 ZIP 備份位置及雜湊，並保存原成果每個檔案的 hash；本輪結束再次核對全部不變。`NEW_manifest.json` 是 byte-identical 副本，仍保留上輪原始 Windows 絕對路徑，沒有重新切分或改寫。

本 ZIP 另附 `data_snapshot/originals/` 中同 40 張原始檔與來源紀錄，僅供保留；實際執行仍使用原 manifest 指向的既有路徑。移到其他電腦時應先恢復 manifest 既有路徑，若必須改寫則另存新資料版本和 hash，不能聲稱原 manifest 不變。不得把 holdout 移入 train 或 val。Manifest 的頂層 fraction 欄位延用 v6 預設，但 smoke 實際分割應以 items 的 20／10／10 計數為準。

本轮固定 validation 條件均改善，不觸發「持續惡化／未低於 baseline」停止條件；但授權僅為 3 epochs 的補測，沒有擴大資料、尺寸或訓練長度。沒有安全性判別器訓練或 P_E。

## 執行與環境

完整命令、UTC 起訖與退出碼見 execution_logs/commands.json。Python 使用既有 bundled interpreter，PYTHONPATH 指向此次工作區 work/python_packages，PYTHONUTF8=1，OMP_NUM_THREADS=4，MKL_NUM_THREADS=4。未再次安裝或更改套件。原生 v6 測試的 Windows 暫存權限問題沿用已記錄的 fixture workaround，不改測試斷言。

`execution_support/` 是此次 orchestrator／稽核腳本；檔案中的工作區路徑需在移動時調整。`source/` 提供此次模型、資料、AMBTC、trainer、evaluator 及測試依赖。僅 best_score 使用 validation；本輪訓練命令沒有 --resume。備份旧權重僅用於保留和訓練結束後的可重現性比對。
