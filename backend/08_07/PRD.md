# PRD：模型重訓練資料源遷移至 Render PostgreSQL

> 本文件為 **產品需求規格書 (Product Requirements Document)**，目標為引導與記錄 `backend/08_07/` 舊專案模型重訓練模組的重構與 Code Review 任務。
> 本次任務已順利將訓練資料源由本地 `Salary_Data2.csv` 遷移至 Render 雲端 PostgreSQL 資料庫（`salary_data2` 資料表），並通過完整 Code Review 與實機測試驗證。

---

## 1. 專案概覽與目標

| 項目 | 說明 |
|---|---|
| 專案名稱 | 薪資預測模型重訓練資料源雲端化遷移 |
| 目標專案位置 | `backend/08_07/`（模型訓練與 FastAPI 服務） |
| 參考連線範例 | `backend/08_13/.env` |
| 核心目的 | 將 `backend/08_07/train_save.py` 從讀取本地 CSV 檔案改為讀取 Render PostgreSQL 資料庫，提升資料即時性與安全性 |
| 環境規格 | Python + `uv` 虛擬環境 + `psycopg2-binary` + `python-dotenv` |
| 任務狀態 | ✅ **重構完成並通過 Code Review** |

---

## 2. 專案系統約束與規則

1. **套件管理約束**：必須全面使用 **uv** 作為套件管理工具（例如 `uv add`、`uv run`），嚴禁使用 `pip install` 或傳統 `venv`。
2. **語言規範**：所有說明與註解必須使用**繁體中文**。
3. **敏感資訊保護**：資料庫連線字串必須儲存於 `.env` 的 `POSTGRES_URL` 變數中，嚴禁將連線密碼硬編碼（Hardcode）於 Python 程式碼中。

---

## 3. Render PostgreSQL 資料庫架構資訊

經由 MCP Server (`render_postgres`) 查詢，Render 雲端資料庫之資料表架構與數據特徵如下：

### 3.1 資料表規格

- **資料庫名稱**：`tvdi_oug1`
- **資料表名稱**：`salary_data2`

### 3.2 欄位結構（Schema）

| 欄位名稱 (Column) | 資料型別 (Type) | 是否可空 (Nullable) | 說明 / 範例值 |
|---|---|---|---|
| `YearsExperience` | `real` (float4) | Yes | 工作年資（例如：`3.0`, `7.8`, `10.0`） |
| `EducationLevel` | `varchar(50)` | Yes | 最高學歷（例如：`'高中以下'`, `'大學'`, `'碩士以上'`） |
| `City` | `varchar(50)` | Yes | 工作/居住城市（例如：`'城市A'`, `'城市B'`, `'城市C'`） |
| `Salary` | `real` (float4) | Yes | 月薪/年薪數據（例如：`45.9`, `80.5`） |

> **注意**：資料庫欄位名稱大小寫與原 `Salary_Data2.csv` 完全一致，SQL 查詢建議對欄位名稱加上雙引號 `SELECT "YearsExperience", "EducationLevel", "City", "Salary" FROM salary_data2;` 以避免大小寫混淆。

---

## 4. Sub-agent 詳細執行步驟 (Step-by-Step Instructions)

Sub-agent 必須依序執行以下 5 大步驟：

### 步驟 1：環境變數與套件準備

1. **確認 `.env` 設定檔**：
   - 確認 `backend/08_07/.env` 已存在（若無則從 `backend/08_13/.env` 複製）。
   - 確認 `backend/08_07/.env` 包含 `POSTGRES_URL` 環境變數（格式：`postgresql://elyse:***@dpg-d9tuqi7qj5pc738hnsa0-a.singapore-postgres.render.com/tvdi_oug1?sslmode=require`）。
2. **檢查並安裝套件**：
   - 進入 `backend/08_07/` 目錄。
   - 使用 uv 安裝資料庫連線與環境變數相關套件：
     ```bash
     uv add psycopg2-binary python-dotenv
     ```

### 步驟 2：重構 `backend/08_07/train_save.py`

修改 `train_save.py` 中的資料載入邏輯：

1. **移除 CSV 檔案讀取**：
   - 移除 `csv_path = os.path.join(current_dir, "Salary_Data2.csv")` 及 `pd.read_csv(csv_path)` 邏輯。
2. **新增 PostgreSQL 資料庫載入邏輯**：
   - 引入 `psycopg2` 與 `from dotenv import load_dotenv`。
   - 執行 `load_dotenv()` 載入 `.env`。
   - 取得 `postgres_url = os.getenv("POSTGRES_URL")`，若不存在則拋出明確錯誤提示。
   - 參考 `backend/08_13/connect_db.py` 的連線模式：
     ```python
     import os
     import time
     import joblib
     import psycopg2
     import pandas as pd
     from pandas import DataFrame
     from dotenv import load_dotenv
     from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
     from sklearn.model_selection import train_test_split
     from sklearn.linear_model import LinearRegression, Ridge, Lasso

     def train_and_save_model(
         test_size: float = 0.2,
         random_state: int = 76,
         model_type: str = "LinearRegression",
         alpha: float = 1.0
     ) -> dict:
         load_dotenv()
         postgres_url = os.getenv("POSTGRES_URL")
         if not postgres_url:
             raise ValueError("找不到 POSTGRES_URL，請確認 backend/08_07/.env 檔案存在！")

         print("正在連線至 Render PostgreSQL 資料庫擷取訓練資料...")
         conn = psycopg2.connect(postgres_url)
         cursor = conn.cursor()
         
         # 讀取 salary_data2 資料表
         query = 'SELECT "YearsExperience", "EducationLevel", "City", "Salary" FROM salary_data2;'
         cursor.execute(query)
         rows = cursor.fetchall()
         colnames = [desc[0] for desc in cursor.description]
         
         cursor.close()
         conn.close()
         
         data = pd.DataFrame(rows, columns=colnames)
         print(f"[成功] 從 PostgreSQL 載入 {len(data)} 筆訓練資料！")

         start_time = time.time()
         
         # 後續資料預處理與模型訓練流程保持不變...
     ```
3. **保留特徵工程與模型訓練**：
   - 保持 `EducationLevel` 的 `OrdinalEncoder` 編碼 (`['高中以下','大學', '碩士以上']`)。
   - 保持 `City` 的 `OneHotEncoder` 編碼 (`['城市A', '城市B', '城市C']`)。
   - 保持 `StandardScaler` 標準化與模型擬合。
   - 將訓練好的模型、預處理器與指標寫入 `backend/08_07/salary_model.joblib`。

### 步驟 3：確認與測試 `backend/08_07/app.py`

1. 檢查 `app.py` 呼叫 `train_and_save_model()` 與 `load_model_state()` 時是否流暢運作。
2. 確保在模型檔 `salary_model.joblib` 不存在時，系統能自動觸發 PostgreSQL 資料庫載入並進行首次訓練。

### 步驟 4：執行獨立訓練驗證 (Standalone Verification)

1. 在 `backend/08_07/` 目錄下執行獨立重訓練腳本：
   ```bash
   uv run python train_save.py
   ```
2. **預期結果**：
   - 控制台顯示 `連線至 Render PostgreSQL 資料庫...`
   - 控制台顯示 `[成功] 從 PostgreSQL 載入 36 筆訓練資料！`
   - 控制台顯示 `模型儲存成功！`
   - `backend/08_07/salary_model.joblib` 成功更新。

### 步驟 5：執行 FastAPI API 端點驗證 (API Verification)

1. 啟動 FastAPI 服務或執行推論測試：
   ```bash
   uv run python -c "from app import predict_endpoint, SalaryInput; print(predict_endpoint(SalaryInput(years_experience=5.0, education_level='大學', city='城市A')))"
   ```
2. 驗證是否成功傳回 `predicted_salary` 與 `estimated_annual_salary`。

---

## 5. 驗收標準 (Acceptance Criteria)

Sub-agent 必須逐項核對以下條件，全數通過才視為完成任務：

- [x] `backend/08_07/.env` 已建立且包含有效的 `POSTGRES_URL`。
- [x] `backend/08_07/` 已安裝 `psycopg2-binary` 與 `python-dotenv`。
- [x] `train_save.py` 完全移除對 `Salary_Data2.csv` 的依賴，改為從 Render PostgreSQL 的 `salary_data2` 資料表讀取。
- [x] 使用 `uv run python train_save.py` 可順利完成模型訓練並更新 `salary_model.joblib`。
- [x] FastAPI 服務與推論端點可用 `app.py` 正常運作。
- [x] `/train` 端點可成功線上觸發 PostgreSQL 資料擷取與模型重新訓練。
- [x] `/predict` 端點可正確輸出預測薪資（測試 5 年經驗/大學/城市A，預測月薪 47.48 萬）。
- [x] 程式碼及輸出訊息皆維持繁體中文與良好的例外處理機制。

---

## 6. 給 Sub-agent 的最終執行指令

1. 閱讀本 PRD.md 的完整規範與步驟。
2. 按照 **4. Sub-agent 詳細執行步驟** 依次操作。
3. 執行完畢後，嚴格根據 **5. 驗收標準** 進行測試與報告回報。

---

## 7. Code Review 與驗證報告 (Code Review & Verification Report)

### 7.1 審查總覽

- **審查日期**：2026-08-13
- **審查狀態**：✅ **PASSED (通過並核可)**
- **審查對象**：
  - `backend/08_07/train_save.py`
  - `backend/08_07/app.py`
  - `backend/08_07/.env`

### 7.2 程式碼架構與品質評估

| 評估面向 | 審查結果 | 詳細說明 |
|---|---|---|
| **資安與密碼保護** | 🟢 優良 (Passed) | 敏感資訊（連線密碼）完全自程式碼分離，統一由 `backend/08_07/.env` 的 `POSTGRES_URL` 變數安全管理。 |
| **資料庫存取規範** | 🟢 優良 (Passed) | 使用 `psycopg2.connect()` 連線，SQL 語法正確使用雙引號引號標示大小寫敏感之欄位名稱（`"YearsExperience", "EducationLevel", "City", "Salary"`），且正確釋放 cursor 與 connection 資源。 |
| **例外處理與穩定度** | 🟢 優良 (Passed) | 針對 `.env` 變數缺失與 SQL 讀取失敗設定明確的 `ValueError` 與 `RuntimeError` 捕捉區塊。 |
| **跨平台 Console 相容性** | 🟢 修正完成 (Passed) | 排除特種 Emoji（如 `✅`）對 Windows Standard Code Page (cp950) 造成的 `UnicodeEncodeError`，統一採用標準標籤（如 `[成功]`），確保在任何作業系統終端機皆能穩定輸出。 |
| **模型預測一致性** | 🟢 優良 (Passed) | PostgreSQL 載入之 36 筆數據整合 OrdinalEncoder 與 OneHotEncoder 特徵轉換流程完全順暢，產出模型可正確進行薪資預測。 |

### 7.3 實機執行驗證紀錄 (Execution Proof)

1. **模型重訓練測試 (Standalone Execution)**：
   - **指令**：`uv run python train_save.py`
   - **執行結果**：
     ```text
     正在連線至 Render PostgreSQL 資料庫擷取訓練資料...
     [成功] 從 PostgreSQL 載入 36 筆訓練資料！
     開始訓練 多元線性迴歸 (OLS) (測試集比例:0.2, 隨機種子:76)....
     正在將模型、預處理器與元數據序列化並儲存至 D:\Github\20260703_ai_tvdi\backend\08_07\salary_model.joblib...
     模型儲存成功！
     ```
   - **結果狀態**：`Exit Code: 0` (成功完成)。

2. **預測服務介面測試 (FastAPI Predict Endpoint)**：
   - **測試指令**：
     ```bash
     uv run python -c "from app import predict_endpoint, SalaryInput; print(predict_endpoint(SalaryInput(years_experience=5.0, education_level='大學', city='城市A')))"
     ```
   - **輸出結果**：
     ```text
     predicted_salary=47.48214044556204 estimated_annual_salary=664.7499662378685
     ```
   - **結果狀態**：`Exit Code: 0` (預測結果符合模型係數預期)。
