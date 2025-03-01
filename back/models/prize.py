from tortoise.models import Model
from tortoise import fields
from uuid import uuid4
from back.models.enums import PrizeType


class ActivePrize(Model):
    uuid = fields.UUIDField(pk=True, default=uuid4) #uuid add
    user = fields.ForeignKeyField('models.Users', related_name='prizes')
    prize_type = fields.CharEnumField(enum_type=PrizeType)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "active_prizes"