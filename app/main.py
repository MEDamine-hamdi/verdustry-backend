from fastapi import FastAPI

from app.api.v1 import auth, users

app = FastAPI(title="Verdustry API", version="0.1.0")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}