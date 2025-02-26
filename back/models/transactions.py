from uuid import uuid4
from tortoise import fields, models

from .enums import TransactionStatus, TransactionCurrencyType

class Transactions(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    user_id = fields.ForeignKeyField("models.Users", related_name="transactions")

    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    type = fields.CharEnumField(enum_type=TransactionCurrencyType)
    status = fields.CharEnumField(enum_type=TransactionStatus)

    cryptobot_invoice_id = fields.CharField(max_length=255, null=True)  # ID инвойса в Cryptobot
    cryptobot_check_id = fields.CharField(max_length=255, null=True)    # ID чека в Cryptobot
    spend_id = fields.CharField(max_length=64, null=True) 
    
    created_at = fields.DatetimeField(auto_now_add=True)
    update_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "transactions"


# class Transaction(models.Model):
#     id = fields.UUIDField(pk=True, default=uuid4, unique=True)
#     user = fields.ForeignKeyField("models.Users", related_name="transactions", on_delete=fields.CASCADE)
#     amount = fields.DecimalField(max_digits=18, decimal_places=8)
#     currency = fields.CharEnumField(TransactionCurrencyType, max_length=20)
#     status = fields.CharEnumField(TransactionStatus, default=TransactionStatus.PENDING, max_length=20)
#     cryptobot_invoice_id = fields.CharField(max_length=128, null=True, unique=True)
#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)

#     class Meta:
#         table = "transactions"