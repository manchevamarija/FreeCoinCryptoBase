from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import sqlite3
import random
import hashlib
from datetime import datetime, timedelta

app = FastAPI()

# --------------------
# STATIC & TEMPLATES
# --------------------
app.mount("/static", StaticFiles(directory="domashna3/static"), name="static")
templates = Jinja2Templates(directory="domashna3/templates")

DB_PATH = "crypto.db"

# --------------------
# HELPERS
# --------------------
def get_all_coins(limit=300):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, symbol, name
        FROM coins
        ORDER BY market_cap_rank
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


# --------------------
# HOME
# --------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/za-nas", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


# --------------------
# API: COINS (for dropdowns)
# --------------------
@app.get("/api/coins")
def api_coins():
    coins = get_all_coins(300)
    return [
        {"id": c[0], "symbol": c[1], "name": c[2]}
        for c in coins
    ]


# --------------------
# GRAFICI
# --------------------
@app.get("/grafici", response_class=HTMLResponse)
def grafici(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, market_cap
        FROM coins
        WHERE market_cap IS NOT NULL
        ORDER BY market_cap DESC
        LIMIT 10
    """)
    top = cur.fetchall()

    cur.execute("""
        SELECT id, symbol, name, market_cap
        FROM coins
        WHERE market_cap IS NOT NULL
        ORDER BY market_cap_rank
        LIMIT 100
    """)
    all_cryptos = cur.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "grafici.html",
        {
            "request": request,
            "names": [r[0] for r in top],
            "caps": [r[1] for r in top],
            "all_cryptos": all_cryptos
        }
    )
@app.get("/cryptos", response_class=HTMLResponse)
def cryptos(
    request: Request,
    filter_id: str | None = None,
    page: int = 1
):
    PER_PAGE = 10
    offset = (page - 1) * PER_PAGE

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1️⃣ DROPDOWN LIST (ID + NAME)
    cur.execute("""
        SELECT id, name
        FROM coins
        ORDER BY market_cap_rank
        LIMIT 300
    """)
    all_cryptos = cur.fetchall()

    # 2️⃣ COUNT (за pagination)
    if filter_id:
        cur.execute(
            "SELECT COUNT(*) FROM coins WHERE id = ?",
            (filter_id,)
        )
    else:
        cur.execute("SELECT COUNT(*) FROM coins")

    total = cur.fetchone()[0]
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    # 3️⃣ MAIN DATA
    if filter_id:
        cur.execute("""
            SELECT id, symbol, name, market_cap, market_cap_rank
            FROM coins
            WHERE id = ?
        """, (filter_id,))
    else:
        cur.execute("""
            SELECT id, symbol, name, market_cap, market_cap_rank
            FROM coins
            ORDER BY market_cap_rank
            LIMIT ? OFFSET ?
        """, (PER_PAGE, offset))

    cryptos = cur.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "cryptos.html",
        {
            "request": request,
            "cryptos": cryptos,
            "all_cryptos": all_cryptos,
            "selected": filter_id,
            "page": page,
            "total_pages": total_pages
        }
    )


# --------------------
# LSTM VIEW
# --------------------
@app.get("/lstm", response_class=HTMLResponse)
def lstm_view(request: Request, coin: str | None = None):
    coins_raw = get_all_coins()

    all_coins = [
        {"id": c[0], "symbol": c[1], "name": c[2]}
        for c in coins_raw
    ]

    selected_coin = next(
        (c for c in all_coins if c["id"] == coin),
        all_coins[0] if all_coins else None
    )

    return templates.TemplateResponse(
        "lstm.html",
        {
            "request": request,
            "all_coins": all_coins,
            "selected_coin": selected_coin
        }
    )


# --------------------
# LSTM API (mock but per-coin)
# --------------------
@app.post("/lstm/predict")
def lstm_predict(payload: dict = Body(...)):
    horizon = int(payload.get("horizon_value", 7))
    coin_id = payload.get("coin_id", "bitcoin")

    seed = int(hashlib.md5(coin_id.encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    history_days = 30
    history_dates = [
        (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in reversed(range(history_days))
    ]

    prices = [rnd.randint(20000, 50000)]
    for _ in range(history_days - 1):
        prices.append(prices[-1] + rnd.randint(-500, 500))

    future_dates = [
        (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(1, horizon + 1)
    ]

    last_price = prices[-1]
    predictions = []
    for _ in range(horizon):
        last_price += rnd.randint(-400, 600)
        predictions.append(last_price)

    return {
        "symbol": coin_id,
        "history_dates": history_dates,
        "history_prices": prices,
        "future_dates": future_dates,
        "predictions": predictions
    }


# --------------------
# SENTIMENT VIEW
# --------------------
@app.get("/sentiment", response_class=HTMLResponse)
def sentiment_view(request: Request):
    return templates.TemplateResponse("sentiment.html", {"request": request})


# --------------------
# SENTIMENT API ✅ PER COIN
# --------------------
@app.get("/api/sentiment")
def sentiment_api(coin: str):
    seed = int(hashlib.md5(coin.upper().encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    positive = rnd.randint(40, 70)
    neutral = rnd.randint(10, 30)
    negative = 100 - positive - neutral

    return {
        "labels": ["Positive", "Neutral", "Negative"],
        "values": [positive, neutral, negative]
    }


# --------------------
# ON-CHAIN VIEW
# --------------------
@app.get("/on-chain", response_class=HTMLResponse)
def onchain_view(request: Request):
    coins_raw = get_all_coins(300)

    all_cryptos = [
        {"id": c[0], "symbol": c[1], "name": c[2]}
        for c in coins_raw
    ]

    return templates.TemplateResponse(
        "on-chain.html",
        {
            "request": request,
            "all_cryptos": all_cryptos
        }
    )



@app.get("/api/onchain")
def onchain_api(coin: str):
    seed = int(hashlib.md5(coin.lower().encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    opinions = [
        {
            "opinion": "Strong network activity detected",
            "sentiment": "Positive",
            "source": "Glassnode"
        },
        {
            "opinion": "Transaction volume increasing steadily",
            "sentiment": "Neutral",
            "source": "CoinMetrics"
        },
        {
            "opinion": "Fees slightly elevated",
            "sentiment": "Negative",
            "source": "CryptoQuant"
        }
    ]

    rnd.shuffle(opinions)
    return opinions



# --------------------
# TECH ANALYSIS VIEW
# --------------------

@app.get("/api/tech")
def tech_api(coin: str):
    seed = int(hashlib.md5(coin.lower().encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    labels = ["D1", "D2", "D3", "D4", "D5"]

    sma = [rnd.randint(40, 60) for _ in range(5)]
    ema = [rnd.randint(45, 65) for _ in range(5)]
    rsi = rnd.randint(25, 80)

    return {
        "labels": labels,
        "sma": sma,
        "ema": ema,
        "rsi": rsi
    }


@app.get("/tech-analysis", response_class=HTMLResponse)
def tech_analysis(request: Request):
    coins_raw = get_all_coins(300)

    all_cryptos = [
        {"id": c[0], "symbol": c[1], "name": c[2]}
        for c in coins_raw
    ]

    return templates.TemplateResponse(
        "tech-analysis.html",
        {
            "request": request,
            "all_cryptos": all_cryptos
        }
    )



# --------------------
# STRATEGY ANALYSIS
# --------------------
def sma_series(prices, window=5):
    out = [None] * len(prices)
    for i in range(window - 1, len(prices)):
        out[i] = sum(prices[i - window + 1:i + 1]) / window
    return out

def rsi_series(prices, period=5):
    out = [None] * len(prices)
    for i in range(period, len(prices)):
        gains = losses = 0
        for j in range(i - period + 1, i + 1):
            diff = prices[j] - prices[j - 1]
            if diff > 0:
                gains += diff
            else:
                losses += abs(diff)
        rs = gains / losses if losses else 0
        out[i] = 100 - (100 / (1 + rs)) if losses else 100
    return out

def ema_series(prices, span):
    out = [None] * len(prices)
    alpha = 2 / (span + 1)
    ema = prices[0]
    out[0] = ema
    for i in range(1, len(prices)):
        ema = alpha * prices[i] + (1 - alpha) * ema
        out[i] = ema
    return out

def macd_series(prices):
    ema12 = ema_series(prices, 12)
    ema26 = ema_series(prices, 26)
    macd = [ema12[i] - ema26[i] if ema12[i] and ema26[i] else None for i in range(len(prices))]
    signal = ema_series([m or 0 for m in macd], 9)
    hist = [(macd[i] - signal[i]) if macd[i] and signal[i] else None for i in range(len(prices))]
    return macd, signal, hist


@app.get("/analysis-view", response_class=HTMLResponse)
def analysis_view(request: Request):
    prices = [30000, 30200, 30450, 30300, 30500, 30700]
    labels = list(range(1, len(prices) + 1))

    return templates.TemplateResponse(
        "analysis.html",
        {
            "request": request,
            "labels": labels,
            "prices": prices,
            "sma5": sma_series(prices),
            "rsi5": rsi_series(prices),
            "macd": macd_series(prices)[0],
            "signal": macd_series(prices)[1],
            "hist": macd_series(prices)[2],
        }
    )
