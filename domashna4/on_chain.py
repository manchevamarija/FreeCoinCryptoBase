import requests
import pandas as pd

# Helper: safe GET with JSON
def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_hashrate():
    data = safe_get("https://api.blockchain.info/charts/hash-rate?timespan=30days&format=json")
    return data["values"][-1]["y"] if data and "values" in data else 0

def get_active_addresses():
    data = safe_get("https://api.blockchain.info/charts/n-unique-addresses?timespan=30days&format=json")
    return data["values"][-1]["y"] if data and "values" in data else 0

def get_tx_count():
    data = safe_get("https://api.blockchain.info/charts/n-transactions?timespan=30days&format=json")
    return data["values"][-1]["y"] if data and "values" in data else 0

def get_mvrv():
    market = safe_get("https://api.blockchain.info/charts/market-price?timespan=30days&format=json")
    realized = safe_get("https://api.blockchain.info/charts/cost-per-transaction?timespan=30days&format=json")
    if market and realized and market.get("values") and realized.get("values"):
        market_price = market["values"][-1]["y"]
        realized_price = realized["values"][-1]["y"]
        return market_price / realized_price if realized_price else 0
    return 0

def get_tvl():
    data = safe_get("https://api.llama.fi/charts/bitcoin")
    return data[-1]["totalLiquidityUSD"] if data and isinstance(data, list) else 0

def get_whale_alert():
    data = safe_get("https://api.whale-alert.io/v1/transactions?api_key=demo&min_value=5000000")
    return len(data.get("transactions", [])) if data else 0

def get_nvt():
    ticker = safe_get("https://api.blockchain.info/ticker")
    vol = safe_get("https://api.blockchain.info/charts/output-volume?timespan=7days&format=json")
    if ticker and vol and vol.get("values"):
        price = ticker["USD"]["last"]
        volume = vol["values"][-1]["y"]
        return price / volume if volume else 0
    return 0

def analyze_onchain():
    return {
        "hashrate": get_hashrate(),
        "active_addresses": get_active_addresses(),
        "transaction_count": get_tx_count(),
        "tvl": get_tvl(),
        "whale_movements": get_whale_alert(),
        "nvt": get_nvt(),
        "mvrv": get_mvrv()
    }

if __name__ == "__main__":
    onchain = analyze_onchain()
    print("\nON-CHAIN\n")
    print(pd.DataFrame([onchain]).T)