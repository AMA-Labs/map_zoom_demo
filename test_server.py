from fastapi import FastAPI

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Test Server API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_server:app", host="0.0.0.0", port=8001, reload=True)
