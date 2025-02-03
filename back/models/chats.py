from uuid import uuid4
from tortoise import fields, models

class Chats(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    deal = fields.OneToOneField("models.Deals", related_name="chat")
    messages = fields.JSONField(default=list)

    is_pinned = fields.BooleanField(default=False)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "chats"