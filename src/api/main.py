from contextlib import asynccontextmanager
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.config.database import engine
from src.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AtenDAI",
    description="Sistema multiagente de atendimento via WhatsApp",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["infra"])
async def health_check() -> JSONResponse:
    settings = get_settings()
    result: dict[str, Any] = {"status": "ok", "services": {}}
    http_status = 200

    # Infraestrutura: capturamos Exception genérica intencionalmente —
    # qualquer falha de conectividade deve degradar o health check.

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        result["services"]["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001
        result["services"]["postgres"] = f"error: {exc}"
        result["status"] = "degraded"
        http_status = 503

    try:
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        result["services"]["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        result["services"]["redis"] = f"error: {exc}"
        result["status"] = "degraded"
        http_status = 503

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(
                f"http://{settings.chroma_host}:{settings.chroma_port}/api/v1/heartbeat"
            )
            resp.raise_for_status()
        result["services"]["chromadb"] = "ok"
    except Exception as exc:  # noqa: BLE001
        result["services"]["chromadb"] = f"error: {exc}"
        result["status"] = "degraded"
        http_status = 503

    return JSONResponse(content=result, status_code=http_status)
