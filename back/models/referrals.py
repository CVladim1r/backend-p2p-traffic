from uuid import uuid4
from tortoise import fields, models

class Referrals(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    referrer_id = fields.ForeignKeyField("models.Users", related_name="referred_users")
    referred_id = fields.ForeignKeyField("models.Users", related_name="referrers")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "referrals"