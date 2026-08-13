# Python 連接 Render PostgreSQL 教學

> 這是一份給學生的 Step-by-Step 教學，教大家如何從 Python 連線到 Render 雲端平台上的 PostgreSQL 資料庫，並用 `.env` 檔案保護資料庫密碼。
> 全篇使用 **uv** 管理套件，**不需要**用到舊式的 pip 安裝方式。

---

## 1. 前言 / 學習目標

這份文件會帶你完成三件事：

1. **取得** Render 上 PostgreSQL 資料庫的連線資訊。
2. **建立**一個 Python 專案，並用 **uv** 安裝必要的套件。
3. **連上**資料庫，並學會用 `.env` 檔案把密碼藏起來，不要讓密碼外洩。

學完之後，你就具備「從 Python 連雲端資料庫」的基本能力，之後做任何需要存資料的專案（記帳、聊天機器人、購物網站……）都用得上。

---

## 2. 什麼是 Render PostgreSQL？

**白話解釋**：Render 是一個雲端平台，就像「租一台永遠開機的電腦」給你。你在上面開一個 **PostgreSQL** 資料庫，資料就存在雲端，任何有網路的人（用對密碼的人）都能連上去讀寫資料。

**PostgreSQL（簡稱 PG）** 是一種很受歡迎的「關聯式資料庫」，類似 Excel，但可以用程式（SQL）來查詢、新增、修改、刪除資料。

你不需要自己安裝 PostgreSQL，Render 會幫你管理好；你只需要知道「怎麼從你的 Python 程式連上去」。

---

## 3. 取得連線資訊

### 3.1 找到你的資料庫

1. 登入 [Render Dashboard](https://dashboard.render.com)。
2. 左側選單點 **Databases** → 點你的 PostgreSQL 服務名稱。
3. 頁面上方會有一個 **Connect** 區塊，點開它。
4. 找到 **External Database URL**（外部連線網址），**把整串複製下來**。

> ⚠️ 這串字串**包含你的資料庫密碼**！複製時不要貼到聊天室、不要截圖傳給別人、不要推上 GitHub。

### 3.2 連線字串長這樣

複製下來的東西大致長這樣（下面只是示意，密碼已改成 `xxxxxx`）：

```text
postgresql://students_user:xxxxxx@dpg-abcdefg-a.oregon-postgres.render.com:5432/students_db?sslmode=require
```

| 欄位 | 範例值 | 白話解釋 |
|---|---|---|
| `postgresql://` | 固定開頭 | 告訴程式「我要連 PostgreSQL」 |
| `students_user` | 使用者名稱 | 登入資料庫的帳號 |
| `xxxxxx` | 密碼 | 登入資料庫的鑰匙，**不要外流** |
| `dpg-abcdefg-a.oregon-postgres.render.com` | 主機位置 | 資料庫這台雲端電腦的「住址」 |
| `5432` | 連接埠 | PostgreSQL 預設的「門口編號」 |
| `students_db` | 資料庫名稱 | 你想連進哪一個資料庫 |

---

## 4. 建立專案與安裝套件

### 4.1 準備工作：確認你有 uv

在終端機（Windows 是 PowerShell，macOS 是 Terminal）輸入：

```bash
uv --version
```

如果有印出版本號碼（例如 `uv 0.5.x`），代表 uv 已安裝。如果沒有，請先跟老師確認安裝方式。

### 4.2 進入專案資料夾

假設你的專案放在 `backend/08_13/`：

```bash
cd backend/08_13
```

> 💡 Windows 與 macOS 都能用 `cd`，只是路徑開頭不同。Windows 常用 `D:\...`，macOS 常用 `/Users/你/...`。

### 4.3 初始化專案（如果是全新的資料夾）

```bash
uv init
```

這會在資料夾內產生 `pyproject.toml`（專案說明檔）和 `main.py`（測試用主程式）。如果資料夾裡已經有專案，可以跳過這一步。

### 4.4 安裝需要的套件

```bash
uv add psycopg2-binary
uv add python-dotenv
```

| 套件 | 用途 | 白話解釋 |
|---|---|---|
| `psycopg2-binary` | PostgreSQL 連線驅動 | 讓 Python 能跟 PostgreSQL「講話」 |
| `python-dotenv` | 讀取 `.env` 檔案 | 幫你把藏在 `.env` 的密碼讀出來 |

> `-binary` 版本代表內建好編譯好的程式，初學者不用煩惱安裝編譯器，最容易成功。

---

## 5. 用 `.env` 保護密碼（重點！）

### 5.1 為什麼不能把密碼寫死在程式碼裡？

想像你家的鑰匙：
- ❌ **寫在程式碼裡** ＝ 把鑰匙直接掛在門口，誰路過都能拿走。如果程式碼被推上 GitHub、或螢幕錄影被看到，密碼就洩漏了。
- ✅ **放在 `.env`** ＝ 鑰匙藏在保險箱，程式要用時再拿出來。`.env` 不會被上傳到 GitHub，別人看不到。

**具體風險**：一旦密碼外流，任何人都能連到你的資料庫，偷看、刪除、竄改你的資料，後果很嚴重。

### 5.2 建立 `.env` 檔案

在專案根目錄（`backend/08_13/`）用 VS Code 或記事本新建一個檔名為 `.env` 的檔案，內容：

```env
POSTGRES_URL=postgresql://你的使用者:你的密碼@你的主機:5432/你的資料庫名稱
```

把 `你的使用者`、`你的密碼` 等換成第 3 節複製下來的 **External Database URL** 整串內容。

> ⚠️ 注意事項：
> - 檔名開頭有「點」，不要打成 `env.txt`。
> - 等號 `=` 兩邊**不要**加空格。
> - 不要用雙引號把整串包起來（除非內容本身有特殊字元）。

### 5.3 建立 `example.env` 當模板

再建立一個 `example.env`，內容只放欄位名稱和占位值（**不含真實密碼**），方便別人複製成自己的 `.env`：

```env
POSTGRES_URL=postgresql://使用者名稱:密碼@主機位置:5432/資料庫名稱
```

這樣萬一有人拿到你的專案，只要 `cp example.env .env` 再填上自己的資料即可。

### 5.4 建立 `.gitignore`，不讓密碼被推上 GitHub

在專案根目錄建立 `.gitignore`，內容：

```text
.env
.env.*
```

> `.env` 與所有 `.env.*`（如 `.env.local`）都會被 Git 忽略，**不會**被推到 GitHub。`example.env` 因為不在忽略規則內，所以可以被提交，作為模板給大家參考。

> ✅ 雙重保護：`.env` 藏密碼（不被上傳）＋ `.gitignore` 擋上傳（不小心也不怕）。兩個都要做。

---

## 6. 撰寫連線程式碼

在專案根目錄建立 `connect_db.py`，貼上以下完整範例：

```python
# connect_db.py
import os                                   # 讀取作業系統的環境變數
import psycopg2                             # PostgreSQL 連線驅動
from dotenv import load_dotenv              # 讀取 .env 檔案的工具

# 1. 讀取 .env 檔案（讓 os.getenv 找得到 POSTGRES_URL）
load_dotenv()

# 2. 從環境變數取得連線字串
postgres_url = os.getenv("POSTGRES_URL")

# 3. 檢查有沒有讀到（安全起見）
if postgres_url is None:
    raise SystemExit("找不到 POSTGRES_URL，請確認 .env 檔案存在且變數名稱正確！")

try:
    # 4. 建立連線
    conn = psycopg2.connect(postgres_url)
    print("✅ 連線成功！")

    # 5. 建立 cursor（可以想像成「指揮員」，幫你送 SQL 指令給資料庫）
    cursor = conn.cursor()

    # 6. 執行 SQL：詢問資料庫版本，確認真的連上了
    cursor.execute("SELECT version();")
    version = cursor.fetchone()

    print("PostgreSQL 版本：", version[0])

    # 7. 關閉 cursor 與連線（用完要關門，釋放資源）
    cursor.close()
    conn.close()
    print("🔌 連線已關閉。")

except psycopg2.Error as e:
    print("❌ 連線失敗：", e)
```

**一行一行看重點：**

| 行 | 在做什麼 |
|---|---|
| `load_dotenv()` | 把 `.env` 的內容載入，程式才找得到變數 |
| `os.getenv("POSTGRES_URL")` | 取出 `.env` 裡 `POSTGRES_URL` 的值（整串連線字串） |
| `psycopg2.connect(postgres_url)` | 拿連線字串去跟資料庫「打招呼」，成功就建立連線 |
| `cursor.execute(...)` | 送 SQL 指令給資料庫執行 |
| `cursor.close()` / `conn.close()` | 用完關閉，避免資源被占用 |

> 💡 進階小知識：把 `cursor` 和 `conn` 寫在 `with` 區塊裡，Python 結束時會自動關閉，更不容易漏關。上述範例用 `try/except` 搭配手動關閉，兩者都是常見做法。

---

## 7. 執行與驗證

在專案根目錄執行：

```bash
uv run python connect_db.py
```

### 預期輸出（代表成功）

```text
✅ 連線成功！
PostgreSQL 版本： PostgreSQL 16.x on x86_64-...
🔌 連線已關閉。
```

### 判定標準

看到上面 **「✅ 連線成功！」** 以及 **PostgreSQL 版本**，代表你已經成功從 Python 連上 Render 的雲端資料庫了！恭喜 🎉

---

## 8. 常見錯誤排除

| 錯誤訊息（片段） | 原因 | 解法 |
|---|---|---|
| `psycopg2.OperationalError: connection failed` | 連線字串錯誤、主機不通或密碼錯誤 | 回到 Render 重新複製完整的 **External Database URL**，確認 `.env` 沒有打錯字、沒有多餘空格 |
| `NameError: name 'load_dotenv' is not defined` | 忘了安裝或匯入 `python-dotenv` | 執行 `uv add python-dotenv`，並確認程式裡有 `from dotenv import load_dotenv` |
| 印出 `None` 或 `找不到 POSTGRES_URL` | 變數名稱打錯，或 `.env` 不在同一層資料夾 | 確認 `.env` 的變數名稱與程式碼都是 `POSTGRES_URL`，且 `.env` 與 `connect_db.py` 放在同一層 |
| `SSL connection error` | Render 強制要求 SSL 加密連線 | 在連線字串最後加上 `?sslmode=require`（見下方範例） |

需要 SSL 時的連線字串範例：

```env
POSTGRES_URL=postgresql://使用者:密碼@主機:5432/資料庫?sslmode=require
```

### 除錯小技巧

- 在 `connect_db.py` 的第一行 `load_dotenv()` 之後，暫時加上 `print(postgres_url)` 確認讀到的值是不是正確的連線字串（確定後再刪掉這行，避免印出密碼）。

---

## 9. 小作業（挑戰題）

試著自己完成以下練習，把結果寫出來或跟同學分享：

### 作業一：建立一張資料表
在 `connect_db.py` 中，用 `cursor.execute` 執行以下 SQL，建立一張 `students` 表格（記得之後要 `conn.commit()` 才算真正寫入）：

```sql
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER
);
```

### 作業二：插入並查詢資料
插入一筆資料，再把它查出來印在畫面上：

```sql
INSERT INTO students (name, score) VALUES ('小明', 95);
SELECT * FROM students;
```

> 💡 提示：`cursor.fetchall()` 可以一次取出所有查詢結果。

### 作業三（進階）：防止 SQL 注入
不要用「字串相加」拼 SQL，改用**參數化查詢**，例如：

```python
cursor.execute("INSERT INTO students (name, score) VALUES (%s, %s);", (name, score))
```

想一想：為什麼直接拼字串很危險？（提示：如果輸入的 `name` 是 `'); DROP TABLE students;--` 會發生什麼事？）

---

## 10. 延伸閱讀 / 參考連結

- [Render 官方文件（Databases）](https://render.com/docs/databases)
- [psycopg2 官方文件](https://www.psycopg.org/docs/)
- [uv 官方文件](https://docs.astral.sh/uv/)
- [python-dotenv（GitHub）](https://github.com/theskumar/python-dotenv)

---

## 結語與安全提醒

恭喜你完成 Python 連接 Render PostgreSQL 的學習！

最後再次提醒：
- 🔒 **密碼就是鑰匙**，不要把它寫死在程式碼、不要上傳 GitHub、不要傳給任何人。
- ✅ 使用 `.env` + `.gitignore` 雙重保護，這是專業開發者的標準做法。
- 有問題時，依照第 8 節的錯誤排除逐步檢查，大多能自己解決。
