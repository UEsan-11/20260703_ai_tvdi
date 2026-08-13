# connect_db.py
import os                                   # 讀取作業系統的環境變數
import psycopg2                             # PostgreSQL 連線驅動
from dotenv import load_dotenv              # 讀取 .env 檔案的工具

# 1. 讀取 .env 檔案（讓 os.getenv 找得到 DATABASE_URL）
load_dotenv()

# 2. 從環境變數取得連線字串
database_url = os.getenv("DATABASE_URL")

# 3. 檢查有沒有讀到（安全起見）
if database_url is None:
    raise SystemExit("找不到 DATABASE_URL，請確認 .env 檔案存在且變數名稱正確！")

try:
    # 4. 建立連線
    conn = psycopg2.connect(database_url)
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