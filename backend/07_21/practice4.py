# ============================================================
# 練習 4：台灣股票歷史股價查詢 API（FastAPI + yfinance）
# ============================================================
# 本檔案建立一個 FastAPI 應用程式，提供以下功能：
#   1. 首頁（/）：以 HTML 表單讓使用者輸入股票代碼並選擇查詢期間。
#   2. 查詢端點（/stock）：回傳指定股票在指定期間內的歷史股價
#      （開盤、最高、最低、收盤、成交量）。
#   3. Swagger 文件（/docs）：FastAPI 自動產生的 API 文件。
#
# 依賴套件：fastapi, uvicorn, yfinance
# 啟動方式：python practice4.py 或 uvicorn practice4:app --reload
# ============================================================

from enum import Enum  # 用於建立列舉型別，限定查詢期間的可選值

import yfinance as yf  # Yahoo Finance 套件，用來抓取股票歷史資料
from fastapi import FastAPI, HTTPException, Query  # FastAPI 核心元件
from fastapi.responses import HTMLResponse  # 用於直接回傳 HTML 內容


# ------------------------------------------------------------
# 建立 FastAPI 應用程式實例，並設定 API 中繼資料
# ------------------------------------------------------------
app = FastAPI(
    title="台灣股票資料 API",
    description="依股票代碼查詢最近 1 天、1 星期、1 個月或 1 年的股價。",
    version="1.0.0",
)


# ------------------------------------------------------------
# 定義查詢期間列舉（StockPeriod）
# ------------------------------------------------------------
# 使用 str, Enum 雙重繼承，讓列舉值同時具有字串值，
# 這樣在 FastAPI 的 Query 參數與 JSON 回傳中都能直接使用。
class StockPeriod(str, Enum):
    """yfinance 支援的查詢期間。"""

    one_day = "1d"      # 最近 1 個交易日
    one_week = "5d"     # 最近 5 個交易日（約 1 週）
    one_month = "1mo"   # 最近 1 個月
    one_year = "1y"     # 最近 1 年


# 將列舉值對應到中文標籤，方便在 UI 與回傳結果中顯示
PERIOD_LABELS = {
    StockPeriod.one_day: "1 天",
    StockPeriod.one_week: "1 星期",
    StockPeriod.one_month: "1 個月",
    StockPeriod.one_year: "1 年",
}


# ------------------------------------------------------------
# 核心函式：取得股票歷史股價
# ------------------------------------------------------------
def get_stock_history(
    stock_code: str, period: StockPeriod
) -> list[dict[str, object]]:
    """
    取得台灣股票歷史股價，並轉換成可由 FastAPI 回傳的格式。

    參數：
        stock_code：台灣股票代碼（純數字，如 "2330"）
        period：查詢期間（StockPeriod 列舉值）

    回傳：
        由 dict 組成的列表，每個 dict 包含一筆交易日的
        date、open、high、low、close、volume。
    """
    # 台灣股票在 Yahoo Finance 的代碼格式為「代碼.TW」
    symbol = f"{stock_code}.TW"
    # 使用 yfinance 取得指定期間的歷史價格 DataFrame
    history = yf.Ticker(symbol).history(period=period.value)

    # 將 DataFrame 的每一列轉換為 dict，組成列表回傳
    records: list[dict[str, object]] = []
    for date, row in history.iterrows():
        records.append(
            {
                "date": date.isoformat(),   # 將 Timestamp 轉為 ISO 8601 字串
                "open": float(row["Open"]),  # 開盤價
                "high": float(row["High"]),  # 最高價
                "low": float(row["Low"]),    # 最低價
                "close": float(row["Close"]),# 收盤價
                "volume": int(row["Volume"]),# 成交量
            }
        )
    return records


# ------------------------------------------------------------
# 路由：首頁（/）— 顯示查詢表單
# ------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    """
    顯示簡單的股票期間查詢頁面。

    使用 HTML 表單（GET 方法）將 stock_code 與 period
    作為查詢參數提交到 /stock 端點。
    include_in_schema=False 表示此端點不會出現在 Swagger 文件中。
    """
    return """
    <!doctype html>
    <html lang="zh-Hant">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>台灣股票資料</title>
      </head>
      <body>
        <h1>台灣股票資料</h1>
        <form action="/stock" method="get">
          <label for="stock_code">股票代碼：</label>
          <!-- 輸入 4~6 碼數字的股票代碼，預設為台積電 2330 -->
          <input id="stock_code" name="stock_code" value="2330"
                 pattern="[0-9]{4,6}" maxlength="6" required>
          <br><br>
          <label for="period">查詢期間：</label>
          <!-- 下拉選單提供 4 種查詢期間 -->
          <select id="period" name="period">
            <option value="1d">1 天</option>
            <option value="5d">1 星期</option>
            <option value="1mo" selected>1 個月</option>
            <option value="1y">1 年</option>
          </select>
          <button type="submit">查詢</button>
        </form>
        <p>API 文件：<a href="/docs">/docs</a></p>
      </body>
    </html>
    """


# ------------------------------------------------------------
# 路由：/stock — 查詢股票歷史股價
# ------------------------------------------------------------
@app.get("/stock", summary="查詢台灣股票歷史股價")
def read_stock(
    # stock_code：股票代碼參數，使用正則表達式驗證格式
    stock_code: str = Query(
        default="2330",
        pattern=r"^[0-9]{4,6}$",
        description="台灣股票代碼，例如：2330、2317、0050",
    ),
    # period：查詢期間參數，使用 StockPeriod 列舉限定可選值
    period: StockPeriod = Query(
        default=StockPeriod.one_month,
        description="查詢期間：1d、5d、1mo 或 1y",
    ),
) -> dict[str, object]:
    """
    依股票代碼及指定期間回傳開、高、低、收與成交量。

    回傳 JSON 包含：
        - stock_code：股票代碼
        - symbol：Yahoo Finance 格式的代碼（如 2330.TW）
        - period：查詢期間代碼
        - period_label：查詢期間中文標籤
        - count：回傳的交易日筆數
        - data：歷史股價陣列
    """
    symbol = f"{stock_code}.TW"
    try:
        # 呼叫核心函式取得歷史股價資料
        data = get_stock_history(stock_code, period)
    except Exception as exc:
        # 若 yfinance 連線失敗或資料來源異常，回傳 502 錯誤
        raise HTTPException(status_code=502, detail="目前無法取得股票資料") from exc

    # 若查無資料（例如股票代碼不存在），回傳 404 錯誤
    if not data:
        raise HTTPException(status_code=404, detail="查無股票資料")

    # 回傳完整的查詢結果 JSON
    return {
        "stock_code": stock_code,        # 使用者輸入的股票代碼
        "symbol": symbol,                # Yahoo Finance 代碼
        "period": period.value,          # 查詢期間代碼（如 "1mo"）
        "period_label": PERIOD_LABELS[period],  # 查詢期間中文（如 "1 個月"）
        "count": len(data),              # 交易日筆數
        "data": data,                    # 歷史股價陣列
    }


# ------------------------------------------------------------
# 直接執行此檔案時，啟動 uvicorn 開發伺服器
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn  # ASGI 伺服器，用來執行 FastAPI 應用

    # 啟動開發伺服器，監聽 127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)