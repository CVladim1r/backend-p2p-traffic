from uuid import uuid4
from tortoise import fields, models

from .enums import TransactionCurrencyType

class Users(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    tg_id = fields.BigIntField(index=True, unique=True)
    is_premium = fields.BooleanField(null=True)
    username = fields.CharField(max_length=128, null=True)
    profile_photo = fields.CharField(max_length=65536, null=True)

    rating = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    is_vip = fields.BooleanField(default=False)

    total_sales = fields.DecimalField(max_digits=18, decimal_places=2, default=0.0)

    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    update_at = fields.DatetimeField(auto_now_add=True, null=True)

    class Meta:
        table = "user"
        indexes = ["tg_id"]


class UserBalance(models.Model):
    id = fields.UUIDField(pk=True, default=uuid4, unique=True)
    user = fields.ForeignKeyField("models.Users", related_name="balances", on_delete=fields.CASCADE)
    currency = fields.CharEnumField(TransactionCurrencyType, max_length=20)
    balance = fields.DecimalField(max_digits=18, decimal_places=8, default=0.0)

    reserved = fields.DecimalField(max_digits=20, decimal_places=6, default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_balance"
        unique_together = ("user", "currency")