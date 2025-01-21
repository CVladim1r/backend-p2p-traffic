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
    # return [
    #     {"code": currency.name, "en": currency.label_en, "ru": currency.label_ru}
    #     for currency in TransactionCurrencyType
    # ]

    currency_massive = []
    for currency in TransactionCurrencyType:
        currency_massive.append(f"{currency.name}")
        # currency_massive.append(f"{currency.label_ru}")

    return currency_massive

@router.get(
    "/categories",
    response_model=list[str],
    responses={400: {"model": APIExceptionModel}},
)
async def get_categories() -> list[str]:
    categories = []
    for category in Categories:
        categories.append(f"{category.label_ru})")
    return categories