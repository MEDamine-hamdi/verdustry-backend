from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.api.v1 import auth, users, companies, sites, suppliers, targets, imports, analytics, benchmark, predictions, anomalies, lca_calculations

app = FastAPI(title="Verdustry API", version="0.1.0")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'"
    )
    response.headers["X-XSS-Protection"] = "0"
    return response


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
app.include_router(lca_calculations.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}