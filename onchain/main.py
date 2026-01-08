from fastapi import FastAPI

app = FastAPI()

@app.get("/on-chain")
def root():
    return {"status": "onchain alive"}
