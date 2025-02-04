import logging
import json
import ast

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
    body_text = body.decode("UTF-8")

    if not crypto_service.crypto.check_signature(
        body_text,
        request.headers.get("crypto-pay-api-signature")
    ):
        raise HTTPException(403, "Invalid signature")

    update = Update.parse_raw(body)
    logging.info(f"Update: {update}, body_text: {body_text}")

    if update.update_type == "invoice_paid":
        invoice = update.payload
        logging.info(f"Received invoice: {invoice}")
        user_data = invoice.description
        logging.info(f"Received invoice: {user_data}")

        try:
            if "UserID:" not in user_data:
                raise ValueError("UserID marker not found in description")
            # parts = user_data.split("UserID:")[1].strip()
            # if len(parts) < 2:
            #     raise ValueError("UserID not found in invoice description")
            # dict_str = parts[1].strip)(
            user_id_part = user_data.split("UserID:")[1].strip()
            user_id_dict = eval(user_id_part)  # You can use `json.loads` if it's valid JSON
            if not isinstance(user_id_dict, dict) or "sub" not in user_id_dict:
                raise ValueError("Invalid user data format in invoice description")
            user_id = int(user_id_dict["sub"])
            logging.info(f"Extracted UserID: {user_id}")
        except (ValueError, IndexError, SyntaxError, KeyError) as e:
            logging.error(f"Error parsing user data from description: {user_data}")
            logging.error(f"Error details: {e}")
            raise APIException(status_code=400, error="Invalid or missing UserID in invoice description")
        
        try:
            amount = Decimal(str(invoice.amount))
        except Exception as e:
            logging.error(f"Error parsing invoice amount: {e}")
            raise APIException(status_code=400, error="Invalid invoice amount")
        try:
            await BalanceController.update_balance(
                user_id=user_id,
                currency=invoice.asset,
                amount=amount
            )
            logging.info(f"Balance updated for UserID {user_id} with {amount} {invoice.asset}")

            await Transactions.filter(
                cryptobot_invoice_id=invoice.invoice_id
            ).update(
                status=TransactionStatus.SUCCESSFUL,
            )
            logging.info(f"Transaction {invoice.invoice_id} marked as successful")
        except Exception as e:
            logging.error(f"Error updating balance or transaction: {e}")
            raise APIException(status_code=500, error="Internal server error")


    elif update.update_type == "invoice_expired":
        try:
            invoice = update.payload
            logging.info(f"Invoice expired received: {invoice}")

            await Transactions.filter(cryptobot_invoice_id=invoice.invoice_id).update(
                status=TransactionStatus.FAILED,
                update_at=datetime.utcnow()
            )
            logging.info(f"Transaction {invoice.invoice_id} marked as failed")
        except Exception as e:
            logging.error(f"Error in invoice_expired handling: {e}")
            raise APIException(status_code=500, error="Internal server error")

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
