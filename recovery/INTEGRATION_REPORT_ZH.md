# GAN-PPO-AMBTC：舊參數殘表整合成果（v4）

## 來源及限制
本次依據新找到的單頁《核心訓練殘留資料.pdf》整合。來源 SHA-256：`5c3ddc86452bf54a72836a6da1c1c488bd3af7ec457914214a329258626b1d1d`。檔案沒有訓練權重、模型原始碼、資料切分或原始日誌；若未來找到另一版本，應先按日期與 SHA-256 比對，再變更配置。

## 實際整合到現有 v3 的內容

| 模組 | v4 新增 | 限制 |
|---|---|---|
| PPO | 兩層 256 MLP、正交初始化、共享／分離兩種架構雛形、可計數參數 | 未知原始網路是否共享；均非原始權重 |
| DQN | 兩層 64、四維觀測／四種動作、Kaiming 初始化 | lambda 動作對應仍有殘表／刊本差異；未虛構 security bias |
| U-Net | 依估計 32/64/128/256 建立四層架構與梯度 smoke test | 缺 Cross-Feedback 精確拓撲；未達刊本所報 4.87M，也不執行真正嵌入 |
| SRM | 可載入並固定真實 `[30,1,5,5]` 核的前端 | 原始核係數缺失，拒絕以隨機濾波器代替 |
| 參數 | 新增 `recovered_note_profile.json` 與來源比對 CSV；batch 記載 16 | 舊 C demo 的 batch=8 不覆寫，保留區隔 |
| 資料 | 增加 SHA-256 清冊、重複檢查、可選「NEW」切分及資產清點工具 | 沒有找回 5,000 張原始 test split；不分發 BOSSbase／BOWS-2 |

**計數結果（全為新建、未訓練架構）：** 共用 PPO 67,845；分離 PPO 134,405；DQN 4,740；U-Net 1,926,243。刊本的 PPO 0.12M、U-Net 4.87M 仍屬報告數值，不能由這一頁殘表還原其精確網路。

## 執行與驗收

```bash
make clean && make test
python3 targeted/run_checks.py
python3 recovery/architecture_report.py
python3 -m unittest discover -s recovery -p 'test_*.py' -v
```

已完成舊 C demo 七項測試及新 recovery 八項測試；未重訓、未產生 Table 4/5/10/11 的新性能數字。

若提供合法影像資料夾，可建立新的唯讀資料清冊：

```bash
python3 recovery/dataset_inventory.py --image-root /path/to/images --out-dir /path/to/report
```

只有要進行**新實驗**時才加 `--new-split --seed 2026`；輸出明確標記 NEW，不能充當原始論文 split。未找到原始權重時，不應繼續用 `policy_smoke.txt` 進行論文性能重現。

## 建議下一步（限定範圍）

1. 將這份舊參數殘表保留為獨立來源，搜尋其他電腦中是否有 `.pt/.pth/.ckpt`、原始 Python 模組與 split CSV；使用 `recovery/asset_inventory.py` 做唯讀雜湊清點。
2. 若找到 checkpoint，先比對 shape/state_dict keys 和訓練時間，再決定是否能接入；不要直接假定新建架構與舊權重相容。
3. GitHub 若要更新，將 v4 標為「archived-note architecture scaffold & provenance tools」，仍沿用軟體修正聲明，不稱為論文重現版本。
