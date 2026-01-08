from fastapi import FastAPI

app = FastAPI()

@app.get("/lstm")
def predict():
    return {"price": 42000}
