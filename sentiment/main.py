from fastapi import FastAPI

app = FastAPI()

@app.get("/sentiment")
def sentiment(text: str):
    return {"sentiment": "positive"}
