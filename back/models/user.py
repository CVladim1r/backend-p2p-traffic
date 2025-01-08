import datetime
from uuid import uuid4

from tortoise import fields, models


class User(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    tg_id = fields.BigIntField(index=True, unique=True)
    is_premium = fields.BooleanField(null=True)
    username = fields.CharField(max_length=128, null=True)

    profile_photo = fields.CharField(max_length=128, null=True)

    rating = fields.IntField(null=True)
    is_vip = fields.BooleanField(default=False)

    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    update_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user"
        indexes = ["tg_id"]
