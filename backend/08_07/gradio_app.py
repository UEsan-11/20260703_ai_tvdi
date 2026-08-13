"""薪資預測服務 Gradio 前端介面。

直接使用 backend/08_07/app.py 的預測與訓練函式，不需要另外啟動 FastAPI 服務。

啟動方式：
    uv run python gradio_app.py

手機觀看：
    1. 手機與電腦連上同一個 Wi-Fi。
    2. 瀏覽器輸入「電腦的區域網路 IP + 連接埠」（例如 http://192.168.1.5:7860）。
       實際 IP 會在啟動時的終端機印出。
"""

from __future__ import annotations

import os
import socket

import gradio as gr

from app import SalaryInput, TrainConfig, predict_endpoint, train_endpoint

EDUCATION_LEVELS = ["高中以下", "大學", "碩士以上"]
CITIES = ["城市A", "城市B", "城市C"]
MODEL_TYPES = ["LinearRegression", "Ridge", "Lasso"]

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

:root {
  --ink: #312e81;
  --ink-soft: #6b6aa8;
  --accent: #7c3aed;
  --accent-2: #3b82f6;
}

html, body, .gradio-container {
  font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif !important;
  color: var(--ink) !important;
  background:
    radial-gradient(1100px 520px at -8% -12%, rgba(196, 181, 253, 0.90) 0%, transparent 62%),
    radial-gradient(950px 480px at 108% 6%, rgba(147, 197, 253, 0.92) 0%, transparent 60%),
    radial-gradient(820px 420px at 50% 112%, rgba(199, 210, 254, 0.85) 0%, transparent 55%),
    linear-gradient(155deg, #eef2ff 0%, #f5f3ff 45%, #fdf4ff 100%) !important;
  background-attachment: fixed;
}

.gradio-container {
  max-width: 980px !important;
  margin: 0 auto !important;
}

.app-shell {
  margin: 18px 12px;
  padding: 22px 26px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 24px 60px rgba(124, 58, 237, 0.20);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.hero h1 {
  margin: 0 0 6px 0;
  font-size: 2.1rem;
  font-weight: 900;
  letter-spacing: 0.03em;
  background: linear-gradient(120deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero p {
  margin: 4px 0 0 0;
  color: var(--ink-soft);
  line-height: 1.7;
}

.hero .hero-note {
  font-size: 0.85rem;
  color: #8b8bb8;
}

.action-btn {
  background: linear-gradient(120deg, var(--accent), var(--accent-2)) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 800 !important;
  font-size: 1.05rem !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 28px rgba(124, 58, 237, 0.35);
  transition: transform 0.15s ease, filter 0.15s ease, box-shadow 0.15s ease;
}

.action-btn:hover {
  filter: brightness(1.06);
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(124, 58, 237, 0.42);
}

label, .wrap {
  color: var(--ink) !important;
}

.result-card {
  border-radius: 16px;
  padding: 18px 20px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(59, 130, 246, 0.12) 100%);
  border: 1px solid rgba(124, 58, 237, 0.22);
}

.result-title {
  font-size: 1.05rem;
  font-weight: 800;
  margin-bottom: 8px;
  color: var(--ink);
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.result-table td {
  padding: 4px 0;
  color: var(--ink-soft);
}

.result-table td:last-child {
  text-align: right;
  font-weight: 700;
  color: var(--ink);
}

.salary-big {
  margin-top: 12px;
  font-size: 2.1rem;
  font-weight: 900;
  background: linear-gradient(120deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.salary-sub {
  font-size: 0.95rem;
  color: var(--ink-soft);
  margin-top: 2px;
}

.tip-box {
  margin-top: 10px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(124, 58, 237, 0.08);
  border: 1px dashed rgba(124, 58, 237, 0.35);
  color: var(--ink-soft);
  font-size: 0.9rem;
}

@media (max-width: 640px) {
  .gradio-container {
    padding: 0 !important;
  }
  .app-shell {
    margin: 8px 6px;
    padding: 14px 14px;
    border-radius: 16px;
  }
  .hero h1 {
    font-size: 1.5rem;
  }
  .salary-big {
    font-size: 1.6rem;
  }
}
"""


def predict_salary(years_experience: float, education_level: str, city: str):
    """呼叫 app.py 的預測函式，並回傳精美 HTML 卡片。"""
    try:
        result = predict_endpoint(
            SalaryInput(
                years_experience=float(years_experience),
                education_level=education_level,
                city=city,
            )
        )
    except Exception as exc:  # noqa: BLE001
        raise gr.Error(f"預測失敗：{exc}")

    return f"""
    <div class="result-card">
      <div class="result-title">預測結果</div>
      <table class="result-table">
        <tr><td>工作年資</td><td>{float(years_experience):.1f} 年</td></tr>
        <tr><td>教育程度</td><td>{education_level}</td></tr>
        <tr><td>工作城市</td><td>{city}</td></tr>
      </table>
      <div class="salary-big">NT$ {result.predicted_salary:,.0f}</div>
      <div class="salary-sub">月薪 &nbsp;·&nbsp; 年薪（14 個月）NT$ {result.estimated_annual_salary:,.0f}</div>
    </div>
    """


def train_model(test_size: float, random_state: int, model_type: str, alpha: float):
    """呼叫 app.py 的訓練函式，並回傳精美 HTML 卡片。"""
    try:
        result = train_endpoint(
            TrainConfig(
                test_size=test_size,
                random_state=int(random_state),
                model_type=model_type,
                alpha=alpha,
            )
        )
    except Exception as exc:  # noqa: BLE001
        raise gr.Error(f"訓練失敗：{exc}")

    feature_rows = "".join(
        f"<tr><td>{name}</td><td>{coef:,.4f}</td></tr>"
        for name, coef in result.feature_coefs.items()
    )
    return f"""
    <div class="result-card">
      <div class="result-title">訓練完成</div>
      <table class="result-table">
        <tr><td>模型類型</td><td>{result.model_type}（α = {result.alpha}）</td></tr>
        <tr><td>R² 決定係數</td><td>{result.r2:.4f}</td></tr>
        <tr><td>截距</td><td>{result.intercept:,.4f}</td></tr>
        <tr><td>訓練耗時</td><td>{result.train_time:.3f} 秒</td></tr>
      </table>
      <div class="tip-box"><b>提示</b>：{result.message}</div>
      <div class="result-title" style="margin-top:14px">特徵權重</div>
      <table class="result-table">{feature_rows}</table>
    </div>
    """


def _get_lan_ip() -> str:
    """取得本機區域網路 IP，方便手機連線。"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _find_available_port(start: int = 7860, end: int = 7890) -> int:
    """從指定範圍內找可用連接埠。"""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"找不到可用連接埠，範圍：{start}-{end}")


with gr.Blocks(title="薪資預測服務") as demo:
    with gr.Column(elem_classes=["app-shell"]):
        gr.HTML(
            """
            <section class="hero">
              <h1>薪資預測服務</h1>
              <p>輸入工作年資、教育程度與城市，預測月薪與年薪；也可以重新訓練模型。</p>
              <p class="hero-note">📱 手機連線：手機與電腦連上同一 Wi-Fi，再輸入「電腦 IP:連接埠」即可使用。</p>
            </section>
            """
        )

        with gr.Tab("薪資預測"):
            with gr.Row(equal_height=True):
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
            predict_output = gr.HTML(label="預測結果")
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
            with gr.Row(equal_height=True):
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
            train_output = gr.HTML(label="訓練結果")

            train_btn.click(
                fn=train_model,
                inputs=[test_size_input, random_state_input, model_type_input, alpha_input],
                outputs=[train_output],
            )


if __name__ == "__main__":
    preferred_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    server_port = _find_available_port(start=preferred_port, end=preferred_port + 30)
    lan_ip = _get_lan_ip()

    if server_port != preferred_port:
        print(f"連接埠 {preferred_port} 已被占用，改用 {server_port} 啟動。")
    print(f"本機網頁：http://127.0.0.1:{server_port}")
    print(f"手機連線（同一 Wi-Fi）：http://{lan_ip}:{server_port}")

    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=server_port,
        css=CUSTOM_CSS,
    )
