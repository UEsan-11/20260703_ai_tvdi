"""薪資預測服務 Gradio 前端介面。

透過 HTTP 呼叫本機 FastAPI 後端 (app.py, port 8000)：
    POST /predict  → 預測薪資
    POST /train    → 重新訓練模型

啟動方式：
    1. 先啟動後端：uv run python backend/08_07/app.py
    2. 再啟動前端：uv run python backend/08_07/gradio_app.py
"""

from __future__ import annotations

import os
import socket

import gradio as gr
import requests

API_BASE = os.getenv("SALARY_API_BASE", "http://127.0.0.1:8000")
TIMEOUT = 30

EDUCATION_LEVELS = ["高中以下", "大學", "碩士以上"]
CITIES = ["城市A", "城市B", "城市C"]
MODEL_TYPES = ["LinearRegression", "Ridge", "Lasso"]

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

:root {
  --bg-a: #e8f5e9;
  --bg-b: #c8e6c9;
  --bg-c: #a5d6a7;
  --card: rgba(255, 255, 255, 0.88);
  --ink: #1b5e20;
  --accent: #2e7d32;
  --accent-2: #00897b;
}

html, body, .gradio-container {
  font-family: 'Noto Sans TC', sans-serif !important;
  color: var(--ink);
  background:
    radial-gradient(1200px 480px at -5% -10%, var(--bg-c) 0%, transparent 60%),
    radial-gradient(900px 420px at 105% 10%, var(--bg-b) 0%, transparent 58%),
    linear-gradient(160deg, var(--bg-a) 0%, #f6f7ef 100%);
}

.app-shell {
  max-width: 900px;
  margin: 16px auto;
  padding: 18px;
  border-radius: 18px;
  background: var(--card);
  box-shadow: 0 20px 45px rgba(27, 94, 32, 0.16);
  backdrop-filter: blur(4px);
}

.hero {
  margin-bottom: 8px;
  padding: 12px 8px;
}

.hero h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.hero p {
  margin: 8px 0 0 0;
  color: #3e5a3e;
}

.action-btn {
  background: linear-gradient(120deg, var(--accent), var(--accent-2)) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 24px rgba(46, 125, 50, 0.32);
}

.action-btn:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}
"""


def _call_api(endpoint: str, payload: dict) -> dict:
    """呼叫後端 API，失敗時回傳錯誤訊息字典。"""
    url = f"{API_BASE.rstrip('/')}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        return {"error": f"無法連線後端 {url}，請確認 app.py 已啟動（port 8000）。"}
    except requests.Timeout:
        return {"error": f"後端回應逾時（{TIMEOUT} 秒），請稍後再試。"}
    except requests.HTTPError as exc:
        detail = exc.response.json().get("detail", str(exc)) if exc.response is not None else str(exc)
        return {"error": f"後端回傳錯誤：{detail}"}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"發生未預期錯誤：{exc}"}


def predict_salary(years_experience: float, education_level: str, city: str):
    """呼叫 /predict 並格式化結果。"""
    result = _call_api(
        "/predict",
        {
            "years_experience": years_experience,
            "education_level": education_level,
            "city": city,
        },
    )
    if "error" in result:
        raise gr.Error(result["error"])
    return (
        f"### 預測結果\n"
        f"- 工作年資：{years_experience:.1f} 年\n"
        f"- 教育程度：{education_level}\n"
        f"- 工作城市：{city}\n\n"
        f"**月薪：NT$ {result['predicted_salary']:,.0f}**\n\n"
        f"**年薪（14 個月）：NT$ {result['estimated_annual_salary']:,.0f}**"
    )


def train_model(test_size: float, random_state: int, model_type: str, alpha: float):
    """呼叫 /train 並格式化結果。"""
    result = _call_api(
        "/train",
        {
            "test_size": test_size,
            "random_state": int(random_state),
            "model_type": model_type,
            "alpha": alpha,
        },
    )
    if "error" in result:
        raise gr.Error(result["error"])

    feature_coefs = "".join(
        f"- {name}：{coef:,.4f}\n" for name, coef in result.get("feature_coefs", {}).items()
    )
    return (
        f"### 訓練完成\n"
        f"- 模型類型：{result.get('model_type')}（α = {result.get('alpha')}）\n"
        f"- R² 決定係數：**{result.get('r2'):.4f}**\n"
        f"- 截距：{result.get('intercept'):,.4f}\n"
        f"- 訓練耗時：{result.get('train_time'):.3f} 秒\n"
        f"- 提示：{result.get('message')}\n\n"
        f"#### 特徵權重\n{feature_coefs}"
    )


def _find_available_port(start: int = 7860, end: int = 7890) -> int:
    """從指定範圍內找可用連接埠。"""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"找不到可用連接埠，範圍：{start}-{end}")


with gr.Blocks(title="薪資預測服務", css=CUSTOM_CSS) as demo:
    with gr.Column(elem_classes=["app-shell"]):
        gr.HTML(
            f"""
            <section class="hero">
              <h1>薪資預測服務</h1>
              <p>前端介面（Gradio）呼叫本機 FastAPI 後端（{API_BASE}），可預測薪資或重新訓練模型。</p>
            </section>
            """
        )

        with gr.Tab("薪資預測"):
            with gr.Row():
                years_input = gr.Slider(
                    label="工作年資（年）",
                    minimum=0.0,
                    maximum=50.0,
                    step=0.5,
                    value=5.0,
                )
                edu_input = gr.Dropdown(
                    label="教育程度",
                    choices=EDUCATION_LEVELS,
                    value="大學",
                )
                city_input = gr.Dropdown(
                    label="工作城市",
                    choices=CITIES,
                    value="城市A",
                )
            predict_btn = gr.Button("開始預測", elem_classes=["action-btn"])
            predict_output = gr.Markdown(label="預測結果")
            gr.Examples(
                examples=[
                    [3.0, "大學", "城市A"],
                    [10.0, "碩士以上", "城市B"],
                    [1.5, "高中以下", "城市C"],
                ],
                inputs=[years_input, edu_input, city_input],
            )

            predict_btn.click(
                fn=predict_salary,
                inputs=[years_input, edu_input, city_input],
                outputs=[predict_output],
            )

        with gr.Tab("模型訓練"):
            with gr.Row():
                test_size_input = gr.Slider(
                    label="測試集比例",
                    minimum=0.1,
                    maximum=0.5,
                    step=0.05,
                    value=0.2,
                )
                random_state_input = gr.Number(
                    label="隨機種子",
                    value=76,
                    precision=0,
                    minimum=0,
                )
                model_type_input = gr.Dropdown(
                    label="模型演算法",
                    choices=MODEL_TYPES,
                    value="LinearRegression",
                )
                alpha_input = gr.Slider(
                    label="正則化強度 α（Lasso / Ridge）",
                    minimum=0.001,
                    maximum=100.0,
                    step=0.001,
                    value=1.0,
                )
            train_btn = gr.Button("重新訓練", elem_classes=["action-btn"])
            train_output = gr.Markdown(label="訓練結果")

            train_btn.click(
                fn=train_model,
                inputs=[test_size_input, random_state_input, model_type_input, alpha_input],
                outputs=[train_output],
            )


if __name__ == "__main__":
    preferred_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    server_port = _find_available_port(start=preferred_port, end=preferred_port + 30)
    if server_port != preferred_port:
        print(f"連接埠 {preferred_port} 已被占用，改用 {server_port} 啟動。")

    demo.launch(server_name="127.0.0.1", server_port=server_port)
