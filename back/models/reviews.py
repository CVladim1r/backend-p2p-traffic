from uuid import uuid4, UUID
from tortoise import fields, models


class Reviews(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    deal_uuid = fields.ForeignKeyField("models.Deals", related_name="reviews")
    reviewer_id = fields.ForeignKeyField("models.Users", related_name="given_reviews")
    reviewed_user_id = fields.ForeignKeyField("models.Users", related_name="received_reviews")
    
    rating = fields.IntField()
    comment = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reviews"

    @classmethod
    async def get_full_review(cls, review_uuid: UUID):
        return await cls.get(uuid=review_uuid).prefetch_related(
            "deal_uuid", "reviewer_id", "reviewed_user_id"
        )