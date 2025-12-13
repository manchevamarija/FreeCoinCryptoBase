from fastapi import FastAPI

app = FastAPI()

import sqlite3

def init_db():
    conn = sqlite3.connect("crypto.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coins (
        id TEXT PRIMARY KEY,
        name TEXT,
        symbol TEXT,
        market_cap REAL,
        market_cap_rank INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running successfully!"}
