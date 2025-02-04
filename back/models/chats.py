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

    @property
    def buyer_name(self):
        return self.deal.buyer_id.username  # Предполагается, что в User есть поле 'name'

    @property
    def seller_name(self):
        return self.deal.seller_id.username

    @property
    def buyer_photo_url(self):
        return self.deal.buyer_id.profile_photo  # Предполагается, что в User есть поле 'photo_url'

    @property
    def seller_photo_url(self):
        return self.deal.seller_id.profile_photo