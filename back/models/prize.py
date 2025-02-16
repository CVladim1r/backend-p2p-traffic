from tortoise.models import Model
from tortoise import fields


class ActivePrize(Model):
    user = fields.ForeignKeyField('models.Users', related_name='prizes')
    prize_type = fields.CharField(max_length=50)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "active_prizes"