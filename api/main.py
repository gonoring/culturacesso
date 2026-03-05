import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from api.database import init_db
from api.routes import editais, trail, leads

load_dotenv()
init_db()

logger = logging.getLogger(__name__)

app = FastAPI(title="CulturaAcesso API", version="1.0")


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "0"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS — restrict methods and headers
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS", "https://culturacesso.com.br,http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(editais.router, prefix="/editais", tags=["editais"])
app.include_router(trail.router, prefix="/trilha", tags=["trilha"])
app.include_router(leads.router, prefix="/leads", tags=["leads"])


# Global exception handler — never leak stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor."}
    )


@app.get("/health")
def health():
    return {"status": "ok"}
