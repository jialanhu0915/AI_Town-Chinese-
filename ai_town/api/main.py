from fastapi import FastAPI

app = FastAPI(title="AI Town API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Welcome to AI Town API"}

@app.get("/health")
def health():
    return {"status": "ok"}
