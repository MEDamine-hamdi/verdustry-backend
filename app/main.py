from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, companies, sites, suppliers, targets, imports, analytics, benchmark, predictions,anomalies

app = FastAPI(title="Verdustry API", version="0.1.0")
from app.core.config import settings
print(f"DEBUG FRONTEND_URL = {settings.FRONTEND_URL}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://verdustry-services.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(targets.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(benchmark.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(anomalies.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}