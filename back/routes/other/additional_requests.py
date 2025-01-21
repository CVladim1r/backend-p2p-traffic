from fastapi import APIRouter

from back.models.enums import TransactionCurrencyType, Categories
from back.errors import APIExceptionModel

router = APIRouter() # dependencies=[Depends(JWTBearer())]

@router.get(
    "/transaction_currency_types",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_transaction_currency_types() -> list[str]:
    return [currency.value for currency in TransactionCurrencyType]


@router.get(
    "/categories",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_categories() -> list[str]:
    return [category.value for category in Categories]
