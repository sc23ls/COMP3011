from fastapi import FastAPI

app = FastAPI(title="Forex Analytics API")

@app.get("/")
def root():
    return {"message": "Forex Analytics API running"}