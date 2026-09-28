import uvicorn
from fastapi import FastAPI
from legalEaseAPI.routes import router
from config import FASTAPI_HOST, FASTAPI_PORT

app = FastAPI(title="LegalEase API")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "LegalEase Backend API is up and running."}

if __name__ == "__main__":
    uvicorn.run("legalEaseAPI.main:app", host=FASTAPI_HOST, port=FASTAPI_PORT, reload=True)