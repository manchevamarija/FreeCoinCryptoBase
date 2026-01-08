from fastapi import FastAPI

app = FastAPI()

@app.get("/tech-analysis")
def analyze(prices: list[float]):
    return {
        "rsi": 55,
        "macd": 1.2
    }
