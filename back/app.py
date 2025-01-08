import logging

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from back.auth.auth import JWTBearer
from back.config import TORTOISE_ORM, debug
from back.errors import APIException
from back.routes import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)03d %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)

app_base = "/api/v1/p2p"

app = FastAPI(
    title="P2P Backend",
    description="Backend service for metrics tracking.",
    version="1.0.1",
    docs_url=f"{app_base}/docs",
    debug=debug,
    redoc_url=None,
    openapi_url=f"{app_base}/p2p_openapi.json",

)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Update domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_tortoise(app, add_exception_handlers=True, config=TORTOISE_ORM)


@app.get("/", summary="Root Endpoint", description="Check API health", dependencies=[Depends(JWTBearer())])
async def root():
    return {"message": "P2P backend is running"}


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


app.include_router(router, prefix=app_base)
