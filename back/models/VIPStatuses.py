from uuid import uuid4
from tortoise import fields, models

class VIPStatuses(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    user_id = fields.ForeignKeyField("models.Users", related_name="vip_status")
    
    valid_until = fields.DatetimeField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "vip_statuses"
