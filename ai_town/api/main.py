from fastapi import FastAPI
from ai_town.api.endpoints_retrieval import router as retrieval_router
from ai_town.api.endpoints_rag import router as rag_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(retrieval_router, prefix='/api')
app.include_router(rag_router, prefix='/api')
