from fastapi import APIRouter

from back.models.enums import TransactionCurrencyType, CategoriesAds, TypeUserAcquisition
from back.errors import APIExceptionModel

router = APIRouter()


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
    "/user_acquisition_type",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_user_acquisition_type() -> list[str]:
    return TypeUserAcquisition

@router.get(
    "/categories",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_categories() -> list[str]:
    return CategoriesAds