from uuid import uuid4
from tortoise import fields, models

class Referrals(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4)
    referrer = fields.ForeignKeyField(
        "models.Users", 
        related_name="referrals",
        db_column="referrer_id"
    )
    referred = fields.ForeignKeyField(
        "models.Users", 
        related_name="referred_by",
        db_column="referred_id",
        unique=True
    )
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "referrals"
        indexes = [
            ("referrer_id", "referred_id"),
        ]