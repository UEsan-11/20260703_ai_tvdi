# PRD：Python 連接 Render Postgres 教學文件

> 本文件為**產品需求規格書 (Product Requirements Document)**，用途是指示**另一個 AI 模型**（下稱「執行模型」）產出教學文件。請執行模型嚴格依照本文件的每一項規格來寫作，不得省略、不得自行臆測未定義的行為。

---

## 1. 專案概覽

| 項目 | 內容 |
|---|---|
| 專案名稱 | Python 連接 Render Postgres 教學 |
| 專案位置 | `backend/08_13/` |
| 目標對象 | 學生（初學者，尚未熟悉 Python 套件管理、資料庫連線、環境變數） |
| 核心目的 | 教學生如何從 Python 連線到 Render 雲端平台上的 PostgreSQL 資料庫，並學會用 `.env` 檔案保護資料庫密碼，且能查詢並顯示資料筆數 |
| 最終產出 | `backend/08_13/python連接postgres.md`（單一 Markdown 教學文件） |

### 1.1 為什麼需要這份文件

- 學生手上有 Render 上建立的 PostgreSQL 資料庫，但不知道如何從本地 Python 連上去。
- 學生常直接把資料庫連線字串（含密碼）寫死在程式碼裡，造成密碼外洩風險。
- 需要一份 Step-by-Step、可照著做、可複製貼上且包含查詢資料筆數驗證的教學文件。

### 1.2 專案系統約束（必須遵守）

- 本專案使用 **uv** 作為 Python 虛擬環境管理工具（見根目錄 `AGENTS.md`）。
- 教學文件中的所有指令必須以 **uv** 為主，不得使用 `pip install` 或 `venv` 等舊式做法。
- 文件一律使用**繁體中文**撰寫。

---

## 2. 目標對象分析

| 面向 | 學生特質 |
|---|---|
| Python 程度 | 已會基礎語法（print、變數、import），但不熟悉套件管理 |
| 資料庫經驗 | 幾乎為零，可能連 SQL 都沒寫過 |
| 雲端經驗 | 已依照老師指示在 Render 建立好 PostgreSQL 資料庫，但不清楚連線資訊含義 |
| 作業系統 | 可能為 Windows 或 macOS，文件需相容兩種環境 |
| 學習動機 | 想完成作業，需要「照做就能成功」的明確步驟 |

### 2.1 教學設計原則

1. **步驟式引導**：每一個動作都要有「步驟編號 + 做什麼 + 為什麼 + 預期結果」。
2. **可複製貼上**：所有程式碼、設定檔內容都必須以程式碼區塊呈現，確保複製即可執行。
3. **先理解再動手**：每個關鍵名詞（外部連線字串、環境變數等）都要有一句「白話解釋」。
4. **錯誤排除章節**：列出學生最常遇到的 3 種以上錯誤與解法。
5. **安全意識**：反覆強調密碼保護的重要性，並示範 `.env` + `.gitignore` 雙重保護。

---

## 3. 交付物（Deliverables）

執行模型必須產出以下檔案，放在 `backend/08_13/` 資料夾下：

| 檔案 | 說明 |
|---|---|
| `python連接postgres.md` | 主教學文件（完整內容，下述所有章節皆須涵蓋） |

> 注意：`.env`、`example.env`、`.gitignore`、`connect_db.py` 等**只出現在教學文件的內容中**作為範例展示，執行模型不需要額外建立實際檔案。

---

## 4. 功能需求（Functional Requirements）

教學文件必須教會學生達成以下能力：

### FR-1 取得 Render PostgreSQL 連線資訊
- 教學學生到 Render Dashboard → 自己的 PostgreSQL 服務 → Connect 區塊，找到 **External Database URL**。
- 解釋連線字串的格式與各欄位含義：

  ```
  postgresql://使用者名稱:密碼@主機位置:連接埠/資料庫名稱
  ```

- 用表格說明欄位對應：`使用者名稱`、`密碼`、`主機位置`、`連接埠`、`資料庫名稱`。

### FR-2 使用 uv 建立專案與安裝套件
- 建立專案資料夾 `backend/08_13/`（若不存在）。
- 使用 `uv init` 建立專案（若該資料夾尚未初始化）。
- 使用 `uv add` 安裝下列套件：
  - `psycopg2-binary`（PostgreSQL 連線驅動，binary 版免編譯，最適合初學者）
  - `python-dotenv`（讀取 `.env` 檔案）

### FR-3 用 `.env` 保護資料庫密碼（重點需求）
- 說明為什麼不能把密碼寫死在程式碼裡（用生活化比喻 + 具體風險）。
- 在專案根目錄建立 `.env` 檔案，內容範例：

  ```env
  DATABASE_URL=postgresql://使用者:密碼@host:5432/dbname
  ```

- 建立 `example.env` 作為模板（只含欄位名稱與占位值，不含真實密碼），方便別人複製。
- 建立 `.gitignore`，加入 `.env` 與 `.env.*`（但不忽略 `example.env`），防止密碼被推上 GitHub。
- 教學 `from dotenv import load_dotenv` + `os.getenv()` 的用法。

### FR-4 撰寫 Python 連線與資料查詢程式碼
- 提供一份可執行的 `connect_db.py` 完整範例，包含：
  1. 匯入 `psycopg2`、`os`、`dotenv`。
  2. `load_dotenv()` 載入 `.env`。
  3. `os.getenv("DATABASE_URL")` 取得連線字串。
  4. 用 `psycopg2.connect()` 建立連線。
  5. 建立 cursor 執行 `SELECT version();` 驗證資料庫連線成功。
  6. 執行 SQL 查詢資料表筆數（例如：`SELECT COUNT(*) FROM salary_data2;` 或讀取 rows 後印出資料筆數）。
  7. 以 `with` 區塊或 `try/finally` 確保連線關閉。
- 程式碼需有中文註解，逐行解釋在做什麼。

### FR-5 驗證連線與資料筆數顯示
- 說明執行後預期看到的輸出（包含印出 PostgreSQL 版本字串以及成功讀取到的資料筆數，例如：「✅ 連線成功！資料庫版本：...，成功讀取到 36 筆資料」）。
- 提供一個「如果看到正確版本與資料筆數就代表成功」的判定標準。

### FR-6 錯誤排除
至少收錄以下 3 種常見錯誤的成因與解法：

| 錯誤訊息（片段） | 原因 | 解法 |
|---|---|---|
| `psycopg2.OperationalError: connection failed` | 連線字串錯誤、主機不通、密碼錯誤 | 檢查 `.env` 拼字、External Database URL 是否複製完整 |
| `NameError: name 'load_dotenv' is not defined` | 忘了安裝或匯入 `python-dotenv` | `uv add python-dotenv`，確認 import 正確 |
| `KeyError` / 取到 `None` | `DATABASE_URL` 變數名稱打錯 | 確認 `.env` 的變數名稱與程式碼一致、檔案在同一層資料夾 |
| SSL 相關錯誤 | Render 強制要求 SSL | 於連線字串加上 `?sslmode=require` |

---

## 5. 教學文件章節結構（必要）

執行模型產出的 `python連接postgres.md` 必須包含以下章節，並依序排列：

1. **前言 / 學習目標**：說明這份文件要教什麼、學會之後能做什麼。
2. **什麼是 Render PostgreSQL？**：用 2-3 句話白話介紹雲端資料庫。
3. **取得連線資訊**：對應 FR-1。
4. **建立專案與安裝套件**：對應 FR-2，全程使用 uv。
5. **用 `.env` 保護密碼**：對應 FR-3，此章節需特別詳細。
6. **撰寫連線程式碼**：對應 FR-4，提供完整可執行範例。
7. **執行與資料筆數驗證**：對應 FR-5，印出連線成功訊息與資料庫內的資料筆數（如 36 筆數據）。
8. **常見錯誤排除**：對應 FR-6。
9. **資料查詢延伸技巧**：示範如何使用 SQL 的 `SELECT COUNT(*)` 與 `LIMIT` 進行基礎查詢。
10. **延伸閱讀 / 參考連結**：Render 官方文件、psycopg2 文件、uv 文件等。

---

## 6. 寫作規範（執行模型必須遵守）

1. **語言**：全篇使用繁體中文；程式碼註解可用中文。
2. **口吻**：親切、耐心、像老師對學生講話；避免過度學術。
3. **程式碼**：所有可執行程式碼放入對應語言的程式碼區塊，標註語言（如 `bash`、`python`、`env`、`text`）。
4. **名詞對照**：第一次出現的英文專有名詞（如 `psycopg2`、`Environment Variable`）需附中文或白話解釋。
5. **絕對路徑**：範例中提及檔案位置時，一律使用專案相對路徑（如 `backend/08_13/.env`），並提醒學生 Windows 的實際路徑可能不同。
6. **平台差異**：Windows 與 macOS 指令不同處需並列說明（例如資料夾路徑分隔符號）。
7. **安全提醒**：至少在「.env」章節與「結尾」各出現一次「不要把密碼傳到網路上／推上 GitHub」的警示。

### 6.1 必須出現的關鍵技術內容清單（檢查表）

- [ ] `uv init`
- [ ] `uv add psycopg2-binary`
- [ ] `uv add python-dotenv`
- [ ] `.env` 檔案格式與範例
- [ ] `example.env` 模板
- [ ] `.gitignore` 內容（`.env`、`.env.*`）
- [ ] `load_dotenv()` 用法
- [ ] `os.getenv("DATABASE_URL")` 用法
- [ ] `psycopg2.connect()` 用法
- [ ] `cursor.execute("SELECT version();")` 驗證
- [ ] 執行 SQL 查詢並顯示資料表總筆數（如 `SELECT COUNT(*)` 或 `len(rows)`）
- [ ] `with conn:` / `conn.close()` 資源關閉
- [ ] 至少 3 種錯誤排除

---

## 7. 驗收標準（Acceptance Criteria）

當以下條件全部滿足時，交付才算完成：

- [ ] `backend/08_13/python連接postgres.md` 檔案存在，且非空白。
- [ ] 全篇為繁體中文。
- [ ] 章節結構符合第 5 節的 10 個章節。
- [ ] 所有 uv 指令以 `uv` 開頭，未出現 `pip install`。
- [ ] `.env`、`example.env`、`.gitignore` 的範例內容完整且可照抄。
- [ ] 提供一份包含「資料庫連線 + 印出版本 + 印出資料筆數」可執行的 `connect_db.py` 完整範例。
- [ ] 第 6.1 節檢查表全數勾選（不含小作業，改為資料筆數查詢驗證）。
- [ ] 錯誤排除至少 3 種。

---

## 8. 給執行模型的最終指令

1. 閱讀本 PRD 全部內容。
2. 先在第 6.1 節檢查表挑選技術細節，確保心中有完整藍圖。
3. 依照第 5 節章節順序撰寫 `python連接postgres.md`，寫入 `backend/08_13/`。
4. 完成後自行對照第 7 節驗收標準逐項檢查；若未通過則修正。
5. 輸出時回報：產出的檔案路徑、章節數、是否全數通過驗收標準。

---

## 9. 參考資料

- Render 官方文件（PostgreSQL 頁面）：https://render.com/docs/databases
- psycopg2 文件：https://www.psycopg.org/docs/
- uv 官方文件：https://docs.astral.sh/uv/
- python-dotenv：https://github.com/theskumar/python-dotenv
