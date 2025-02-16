from tortoise.models import Model
from tortoise import fields

from back.models.enums import PrizeType

class ActivePrize(Model):
    user = fields.ForeignKeyField('models.Users', related_name='prizes')
    prize_type = fields.CharEnumField(enum_type=PrizeType)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "active_prizes"