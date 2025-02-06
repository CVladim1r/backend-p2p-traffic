from fastapi import APIRouter

from back.models.enums import TransactionCurrencyType, CategoriesAds
from back.errors import APIExceptionModel

router = APIRouter() # dependencies=[Depends(JWTBearer())]

@router.get(
    "/transaction_currency_types",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_transaction_currency_types() -> list[str]:
    currency_massive = []
    for currency in TransactionCurrencyType:
        currency_massive.append(f"{currency.name}")
    return currency_massive

@router.get(
    "/categories",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_categories() -> list[str]:
    return CategoriesAds