import { useState, useCallback, useEffect, useRef } from 'react'
import './App.css'

const API_BASE = 'https://2026-07-03-tvdi.onrender.com'

interface PredictionResult {
  prediction_id: number
  prediction_label: string
  probabilities: Record<string, number>
}

interface TrainResult {
  status: string
  accuracy: number
  train_time: number
  feature_importances: Record<string, number>
  message: string
}

interface ModelState {
  accuracy: number
  train_time: number
  n_estimators: number
  max_depth: number | null
  test_size: number
  random_state: number
  feature_names: string[]
}

const SPECIES_MAP: Record<string, { cn: string; emoji: string }> = {
  setosa: { cn: '山鳶尾', emoji: '🌿' },
  versicolor: { cn: '變色鳶尾', emoji: '🍁' },
  virginica: { cn: '維吉尼亞鳶尾', emoji: '🪻' },
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

function App() {
  const [activeTab, setActiveTab] = useState<'predict' | 'train'>('predict')

  // --- Predict state ---
  const [sepalLen, setSepalLen] = useState(5.1)
  const [sepalWid, setSepalWid] = useState(3.5)
  const [petalLen, setPetalLen] = useState(1.4)
  const [petalWid, setPetalWid] = useState(0.2)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [predictError, setPredictError] = useState('')

  // --- Train state ---
  const [nEstimators, setNEstimators] = useState(100)
  const [maxDepth, setMaxDepth] = useState(0)
  const [testSize, setTestSize] = useState(0.2)
  const [randomState, setRandomState] = useState(42)
  const [trainResult, setTrainResult] = useState<TrainResult | null>(null)
  const [trainLoading, setTrainLoading] = useState(false)
  const [trainError, setTrainError] = useState('')

  // --- Model state ---
  const [modelState, setModelState] = useState<ModelState | null>(null)

  // Fetch initial model state
  useEffect(() => {
    fetch(`${API_BASE}/openapi.json`)
      .then(r => r.json())
      .then(() => {
        setModelState({
          accuracy: 0.9667,
          train_time: 0.01,
          n_estimators: 100,
          max_depth: null,
          test_size: 0.2,
          random_state: 42,
          feature_names: ['sepal length', 'sepal width', 'petal length', 'petal width'],
        })
      })
      .catch(() => {})
  }, [])

  // --- Predict ---
  const doPredict = useCallback(async (sl: number, sw: number, pl: number, pw: number) => {
    setPredictError('')
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sepal_length: sl,
          sepal_width: sw,
          petal_length: pl,
          petal_width: pw,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: PredictionResult = await res.json()
      setPrediction(data)
    } catch (e) {
      setPredictError(`預測失敗：${e instanceof Error ? e.message : '未知錯誤'}`)
    }
  }, [])

  // Debounced slider values for auto-predict
  const debouncedSliders = useDebounce({ sepalLen, sepalWid, petalLen, petalWid }, 300)
  const didInitPredict = useRef(false)

  useEffect(() => {
    if (!didInitPredict.current) {
      didInitPredict.current = true
      doPredict(debouncedSliders.sepalLen, debouncedSliders.sepalWid, debouncedSliders.petalLen, debouncedSliders.petalWid)
      return
    }
    doPredict(debouncedSliders.sepalLen, debouncedSliders.sepalWid, debouncedSliders.petalLen, debouncedSliders.petalWid)
  }, [debouncedSliders, doPredict])

  // --- Train ---
  const doTrain = useCallback(async () => {
    setTrainLoading(true)
    setTrainError('')
    setTrainResult(null)
    try {
      const res = await fetch(`${API_BASE}/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          n_estimators: nEstimators,
          max_depth: maxDepth,
          test_size: testSize,
          random_state: randomState,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: TrainResult = await res.json()
      setTrainResult(data)
      setModelState({
        accuracy: data.accuracy,
        train_time: data.train_time,
        n_estimators: nEstimators,
        max_depth: maxDepth === 0 ? null : maxDepth,
        test_size: testSize,
        random_state: randomState,
        feature_names: Object.keys(data.feature_importances),
      })
    } catch (e) {
      setTrainError(`訓練失敗：${e instanceof Error ? e.message : '未知錯誤'}`)
    } finally {
      setTrainLoading(false)
    }
  }, [nEstimators, maxDepth, testSize, randomState])

  // --- Render helpers ---
  const renderSlider = (
    label: string,
    enLabel: string,
    value: number,
    onChange: (v: number) => void,
    min: number,
    max: number,
    step: number
  ) => (
    <div className="slider-group">
      <div className="slider-label">
        <span className="name">{label}<span className="en">{enLabel}</span></span>
        <span className="value">{value.toFixed(1)}</span>
      </div>
      <div className="slider-wrapper">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={e => onChange(parseFloat(e.target.value))}
        />
      </div>
    </div>
  )

  const renderPredictionPanel = () => (
    <div className="card">
      <div className="card-title"><span className="step-num">2</span> 預測結果與機率分析</div>

      {predictError && (
        <div className="status-msg error">{predictError}</div>
      )}

      {!prediction && !predictError && (
        <div className="placeholder-state">
          <div className="icon">🔮</div>
          <p className="loading-text">正在連線預測模型...</p>
        </div>
      )}

      {prediction && (
        <div className="fade-in">
          {/* Prediction card */}
          <div className={`prediction-card ${prediction.prediction_label}`}>
            <div className="label-text">預測分析品種</div>
            <div className="species-name">
              {SPECIES_MAP[prediction.prediction_label]?.emoji || ''}{' '}
              {prediction.prediction_label.charAt(0).toUpperCase() + prediction.prediction_label.slice(1)}
              <span className="cn">{SPECIES_MAP[prediction.prediction_label]?.cn || ''}</span>
            </div>
            <div className="prob-text">
              預測機率: <strong>{(prediction.probabilities[prediction.prediction_label] * 100).toFixed(1)}%</strong>
            </div>
          </div>

          {/* Probability bars */}
          <div className="prob-bars">
            {Object.entries(prediction.probabilities).map(([cls, prob]) => (
              <div className="prob-bar-item" key={cls}>
                <div className="bar-header">
                  <span className="cls-name">{cls}</span>
                  <span className="cls-pct">{(prob * 100).toFixed(1)}%</span>
                </div>
                <div className="prob-bar-track">
                  <div
                    className={`prob-bar-fill ${cls}`}
                    style={{ width: `${prob * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  const renderTrainingPanel = () => (
    <div className="card">
      <div className="card-title"><span className="step-num">2</span> 訓練結果與模型評估</div>

      {trainError && (
        <div className="status-msg error">{trainError}</div>
      )}

      {trainResult && (
        <div className="fade-in">
          <div className="status-msg success">
            ✅ {trainResult.message}
          </div>

          <div className="metrics-grid">
            <div className="metric-card accuracy">
              <div className="metric-label">測試集準確度</div>
              <div className="metric-value">{(trainResult.accuracy * 100).toFixed(2)}%</div>
            </div>
            <div className="metric-card time">
              <div className="metric-label">模型訓練耗時</div>
              <div className="metric-value">{trainResult.train_time.toFixed(4)}s</div>
            </div>
            <div className="metric-card trees">
              <div className="metric-label">決策樹數量</div>
              <div className="metric-value">{nEstimators}</div>
            </div>
          </div>

          <div className="metric-row">
            <span>🌲 <strong>最大樹深度:</strong> {maxDepth === 0 ? '無限制' : maxDepth}</span>
            <span>📊 <strong>測試集比例:</strong> {(testSize * 100).toFixed(0)}%</span>
          </div>

          {/* Feature Importance */}
          {Object.keys(trainResult.feature_importances).length > 0 && (
            <div className="importance-section">
              <h4>💡 特徵重要性分析 (Feature Importance)</h4>
              <div className="importance-bars">
                {Object.entries(trainResult.feature_importances)
                  .sort((a, b) => b[1] - a[1])
                  .map(([feature, val], idx) => {
                    const maxVal = Math.max(...Object.values(trainResult.feature_importances))
                    const pct = maxVal > 0 ? (val / maxVal) * 100 : 0
                    return (
                      <div className="importance-bar-item" key={feature}>
                        <div className="bar-header">
                          <span className="feature-name">{feature}</span>
                          <span>{(val * 100).toFixed(1)}%</span>
                        </div>
                        <div className="importance-bar-track">
                          <div
                            className={`importance-bar-fill c${idx}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}
        </div>
      )}

      {!trainResult && !trainError && (
        <div className="placeholder-state">
          <div className="icon">⚙️</div>
          <p>設定超參數後點擊「開始訓練」<br/>即可查看模型評估結果</p>
        </div>
      )}

      {modelState && trainResult && (
        <div className="fade-in" style={{ marginTop: 16 }}>
          <div className="metrics-grid">
            <div className="metric-card accuracy">
              <div className="metric-label">當前準確度</div>
              <div className="metric-value">{(modelState.accuracy * 100).toFixed(2)}%</div>
            </div>
            <div className="metric-card time">
              <div className="metric-label">訓練耗時</div>
              <div className="metric-value">{modelState.train_time.toFixed(4)}s</div>
            </div>
            <div className="metric-card trees">
              <div className="metric-label">決策樹數量</div>
              <div className="metric-value">{modelState.n_estimators}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌸 Iris 鳶尾花機器學習平台</h1>
        <p className="subtitle">
          結合 FastAPI 與 React 的機器學習部署服務，提供即時預測與線上訓練功能
        </p>
        <div className="header-badges">
          <span className="badge">🤖 Random Forest</span>
          <span className="badge">⚡ FastAPI Backend</span>
          <span className="badge">🎨 React Frontend</span>
        </div>
      </header>

      <main className="main-container">
        <div className="tabs-header">
          <button
            className={`tab-btn ${activeTab === 'predict' ? 'active' : ''}`}
            onClick={() => setActiveTab('predict')}
          >
            🔮 即時模型預測
          </button>
          <button
            className={`tab-btn ${activeTab === 'train' ? 'active' : ''}`}
            onClick={() => setActiveTab('train')}
          >
            ⚙️ 線上模型訓練
          </button>
        </div>

        {activeTab === 'predict' && (
          <div className="panel-layout fade-in">
            <div className="card">
              <div className="card-title"><span className="step-num">1</span> 輸入特徵參數</div>
              {renderSlider('花萼長度', 'Sepal Length (cm)', sepalLen, setSepalLen, 0.1, 10, 0.1)}
              {renderSlider('花萼寬度', 'Sepal Width (cm)', sepalWid, setSepalWid, 0.1, 10, 0.1)}
              {renderSlider('花瓣長度', 'Petal Length (cm)', petalLen, setPetalLen, 0.1, 10, 0.1)}
              {renderSlider('花瓣寬度', 'Petal Width (cm)', petalWid, setPetalWid, 0.1, 10, 0.1)}
            </div>
            {renderPredictionPanel()}
          </div>
        )}

        {activeTab === 'train' && (
          <div className="panel-layout fade-in">
            <div className="card">
              <div className="card-title"><span className="step-num">1</span> 調整隨機森林超參數</div>

              <div className="input-group">
                <label className="input-label">決策樹數量 <span className="en">n_estimators</span></label>
                <input
                  type="range"
                  min={10}
                  max={500}
                  step={10}
                  value={nEstimators}
                  onChange={e => setNEstimators(parseInt(e.target.value))}
                />
                <div className="slider-label">
                  <span className="name"></span>
                  <span className="value">{nEstimators}</span>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">最大深度 <span className="en">max_depth (0 = 無限制)</span></label>
                <input
                  type="range"
                  min={0}
                  max={20}
                  step={1}
                  value={maxDepth}
                  onChange={e => setMaxDepth(parseInt(e.target.value))}
                />
                <div className="slider-label">
                  <span className="name"></span>
                  <span className="value">{maxDepth === 0 ? '無限制' : maxDepth}</span>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">測試集比例 <span className="en">test_size</span></label>
                <input
                  type="range"
                  min={0.1}
                  max={0.5}
                  step={0.05}
                  value={testSize}
                  onChange={e => setTestSize(parseFloat(e.target.value))}
                />
                <div className="slider-label">
                  <span className="name"></span>
                  <span className="value">{testSize.toFixed(2)}</span>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">隨機種子 <span className="en">random_state</span></label>
                <input
                  className="number-input"
                  type="number"
                  min={0}
                  value={randomState}
                  onChange={e => setRandomState(parseInt(e.target.value) || 0)}
                />
              </div>

              <button
                className="btn-primary"
                onClick={doTrain}
                disabled={trainLoading}
              >
                {trainLoading ? <><span className="spinner" /> 訓練中...</> : '🚀 開始訓練模型'}
              </button>
            </div>
            {renderTrainingPanel()}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
