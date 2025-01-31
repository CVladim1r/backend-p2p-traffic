import logging

from decimal import Decimal
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from aiocryptopay.models.update import Update

from back.auth.auth import JWTBearer
from back.config import TORTOISE_ORM, CRYPTBOT_WEBHOOK_URL, debug

from back.errors import APIException
from back.routes import router
from back.utils.cryptobot import crypto_service
from back.controllers.balance import BalanceController
from back.models.transactions import Transactions
from back.models.enums import TransactionStatus


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



@app.post("/webhook/cryptobot", summary="Webhook Endpoint", description="Check API health")
async def cryptobot_webhook(request: Request):
    body = await request.body()
    body_text = body.decode("UTF-8")  # Декодируем bytes в строку

    if not crypto_service.crypto.check_signature(
        body_text,
        request.headers.get("crypto-pay-api-signature")
    ):
        raise HTTPException(403, "Invalid signature")
    
    update = Update.parse_raw(body)
    logging.info(f"Update: {update}, body_text: {body_text}")

    if update.update_type == "invoice_paid":
        logging.info(f"Received invoice: {invoice}")

        user_data = update.payload
        try:
            user_id = int(user_data['UserID']['sub'])
        except (ValueError, KeyError):
            raise HTTPException(status_code=400, detail="Invalid or missing UserID in invoice description")

        amount = Decimal(invoice.amount)
        await BalanceController.update_balance(
            user_id=user_id,
            currency=invoice.asset,
            amount=amount
        )

        await Transactions.filter(
            cryptobot_invoice_id=invoice.invoice_id
        ).update(
            status=TransactionStatus.SUCCESSFUL,
            update_at=datetime.utcnow()
        )
    elif update.update_type == "invoice_expired":
        invoice = update.payload
        await Transactions.filter(cryptobot_invoice_id=invoice.invoice_id).update(
            status=TransactionStatus.FAILED,
            update_at=datetime.utcnow()
        )
    
    return {"status": "ok"}


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
