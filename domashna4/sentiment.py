import requests
import pandas as pd
from pytrends.request import TrendReq
from transformers import pipeline

# sentiment model
sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    framework="pt",
    device=-1
)

def get_reddit_sentiment():
    try:
        r = requests.get(
            "https://api.pushshift.io/reddit/search/submission/?subreddit=Bitcoin&size=20"
        ).json()
        titles = [p.get("title", "") for p in r.get("data", [])]
        if not titles:
            return 0
        score = 0
        for t in titles:
            label = sentiment_model(t)[0]["label"]
            score += 1 if label == "POSITIVE" else -1
        return score
    except:
        return 0

def get_news_sentiment():
    try:
        r = requests.get(
            "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=BTC"
        ).json()
        titles = [i["title"] for i in r.get("results", [])]
        if not titles:
            raise Exception("CryptoPanic empty")
    except:
        try:
            import feedparser
        except ImportError:
            return 0
        feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")
        titles = [e.title for e in feed.entries[:15]]
    if not titles:
        return 0
    score = 0
    for t in titles:
        label = sentiment_model(t)[0]["label"]
        score += 1 if label == "POSITIVE" else -1
    return score

def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1&format=json").json()
        return int(r["data"][0]["value"])
    except:
        return 0

def get_google_trends():
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(["Bitcoin"], timeframe="now 7-d")
        data = pytrends.interest_over_time()
        return int(data["Bitcoin"].iloc[-1])
    except:
        return 0

def analyze_sentiment():
    return {
        "reddit_sentiment": get_reddit_sentiment(),
        "news_sentiment": get_news_sentiment(),
        "fear_greed": get_fear_greed(),
        "google_trends": get_google_trends()
    }

if __name__ == "__main__":
    sentiment = analyze_sentiment()
    print("\nSENTIMENT\n")
    print(pd.DataFrame([sentiment]).T)