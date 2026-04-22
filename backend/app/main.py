from fastapi import FastAPI
from .api import receipt_api


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(receipt_api.router)
