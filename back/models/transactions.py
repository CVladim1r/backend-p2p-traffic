from uuid import uuid4
from tortoise import fields, models

from .enums import TransactionStatus, TransactionType

class Transactions(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    user_id = fields.ForeignKeyField("models.Users", related_name="transactions")

    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    type = fields.CharEnumField(enum_type=TransactionType)
    status = fields.CharEnumField(enum_type=TransactionStatus)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "transactions"