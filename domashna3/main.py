from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import math
from fastapi.responses import HTMLResponse

from domashna4.strategy_pattern.factory import StrategyFactory
from domashna4.strategy_pattern.context import AnalysisContext

app = FastAPI()

app.mount("/static", StaticFiles(directory="domashna3/static"), name="static")
templates = Jinja2Templates(directory="domashna3/templates")

DB_PATH = "crypto.db"

SAMPLE_PRICES = [
    30000, 30100, 30250, 30300, 30400,
    30500, 30600, 30700, 30800, 30900
]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/cryptos")
def show_cryptos(request: Request, filter_id: str = None, page: int = 1):
    limit = 20
    offset = (page - 1) * limit

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM coins ORDER BY market_cap_rank LIMIT 200"
    )
    all_cryptos = cursor.fetchall()

    if filter_id:
        cursor.execute("""
            SELECT id, symbol, name, market_cap, market_cap_rank
            FROM coins
            WHERE id = ?
        """, (filter_id,))
        rows = cursor.fetchall()
        total_pages = 1
    else:
        cursor.execute("SELECT COUNT(*) FROM coins")
        total = cursor.fetchone()[0]
        total_pages = (total // limit) + (1 if total % limit else 0)

        cursor.execute("""
            SELECT id, symbol, name, market_cap, market_cap_rank
            FROM coins
            ORDER BY market_cap_rank
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "cryptos.html",
        {
            "request": request,
            "cryptos": rows,
            "all_cryptos": all_cryptos,
            "selected": filter_id,
            "page": page,
            "total_pages": total_pages
        }
    )


@app.get("/za-nas")
def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


@app.get("/grafici")
def show_graphs(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, market_cap
        FROM coins
        WHERE market_cap IS NOT NULL
        ORDER BY market_cap DESC
        LIMIT 10
    """)
    data = cursor.fetchall()
    conn.close()

    names = [row[0] for row in data]
    caps = [row[1] for row in data]

    return templates.TemplateResponse(
        "grafici.html",
        {
            "request": request,
            "names": names,
            "caps": caps
        }
    )


@app.get("/lstm")
def lstm(request: Request):
    return templates.TemplateResponse(
        "lstm.html",
        {
            "request": request,
            "dates": ["2025-01-01", "2025-01-02", "2025-01-03"],
            "true_prices": [30000, 30500, 31000],
            "predicted_prices": [29950, 30600, 30950],
        }
    )


@app.get("/analysis")
def run_analysis(type: str = "RSI"):
    strategy = StrategyFactory.create(type)
    context = AnalysisContext(strategy)
    return {
        "pattern": "Strategy",
        "strategy": type,
        "result": context.execute(SAMPLE_PRICES)
    }


def sma_series(prices, window=5):
    out = [None] * len(prices)
    if window <= 0:
        return out
    for i in range(window - 1, len(prices)):
        out[i] = round(sum(prices[i - window + 1:i + 1]) / window, 2)
    return out


def rsi_series(prices, period=5):
    out = [None] * len(prices)
    if len(prices) < period + 1:
        return out

    for i in range(period, len(prices)):
        gains = 0.0
        losses = 0.0
        for j in range(i - period + 1, i + 1):
            diff = prices[j] - prices[j - 1]
            if diff > 0:
                gains += diff
            else:
                losses += abs(diff)

        avg_gain = gains / period
        avg_loss = losses / period

        if avg_loss == 0:
            out[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            out[i] = round(rsi, 2)

    return out


def ema_series(prices, span):
    out = [None] * len(prices)
    if not prices or span <= 0:
        return out

    alpha = 2 / (span + 1)
    ema = prices[0]
    out[0] = round(ema, 6)

    for i in range(1, len(prices)):
        ema = alpha * prices[i] + (1 - alpha) * ema
        out[i] = round(ema, 6)

    return out


def macd_series(prices, fast=12, slow=26, signal=9):

    if len(prices) < 2:
        n = len(prices)
        return [None]*n, [None]*n, [None]*n

    ema_fast = ema_series(prices, fast)
    ema_slow = ema_series(prices, slow)

    macd_line = [None] * len(prices)
    for i in range(len(prices)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line[i] = None
        else:
            macd_line[i] = round(ema_fast[i] - ema_slow[i], 6)

    macd_for_ema = [0.0 if v is None else float(v) for v in macd_line]
    signal_line_raw = ema_series(macd_for_ema, signal)

    signal_line = [None] * len(prices)
    hist = [None] * len(prices)
    for i in range(len(prices)):
        if macd_line[i] is None or signal_line_raw[i] is None:
            signal_line[i] = None
            hist[i] = None
        else:
            signal_line[i] = round(float(signal_line_raw[i]), 6)
            hist[i] = round(float(macd_line[i]) - float(signal_line[i]), 6)

    return macd_line, signal_line, hist


@app.get("/analysis-view", response_class=HTMLResponse)
def analysis_view(request: Request):
    prices = SAMPLE_PRICES
    labels = list(range(1, len(prices) + 1))

    sma5 = sma_series(prices, window=5)
    rsi5 = rsi_series(prices, period=5)
    macd_line, signal_line, hist = macd_series(prices, fast=12, slow=26, signal=9)

    return templates.TemplateResponse(
        "analysis.html",
        {
            "request": request,
            "labels": labels,
            "prices": prices,
            "sma5": sma5,
            "rsi5": rsi5,
            "macd": macd_line,
            "signal": signal_line,
            "hist": hist,
        }
    )
