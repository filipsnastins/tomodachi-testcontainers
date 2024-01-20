import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
async def hello_api() -> dict:
    greet = os.getenv("GREET", "stranger")
    return {"message": f"Hello from FastAPI, {greet}!"}


@app.get("/health")
async def healthcheck_api() -> dict:
    return {"status": "ok"}
