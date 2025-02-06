from uuid import uuid4
from tortoise import fields, models

from .enums import (
    AdStatus, 
    DealStatus, 
    CategoriesAds, 
    TypeUserAcquisition,
    TransactionCurrencyType
)


class Ads(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    user_id = fields.ForeignKeyField("models.Users", related_name="ads")
    title = fields.CharField(max_length=256)
    description = fields.TextField()
    category = fields.CharEnumField(enum_type=CategoriesAds)     
    type_ads = fields.CharEnumField(enum_type=TypeUserAcquisition)     

    price = fields.DecimalField(max_digits=15, decimal_places=2)
    currency_type = fields.CharEnumField(enum_type=TransactionCurrencyType)
    link_to_channel = fields.CharField(max_length=256)
    guaranteed_traffic = fields.BooleanField(default=False)
    minimum_traffic = fields.IntField(null=True)
    maximum_traffic = fields.IntField(null=True)

    conditions = fields.TextField(null=True)
    status = fields.CharEnumField(enum_type=AdStatus)
    is_paid_promotion = fields.BooleanField(default=False)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "ads"


class Deals(models.Model):
    uuid = fields.UUIDField(pk=True, default=uuid4, unique=True)
    ad_uuid = fields.ForeignKeyField("models.Ads", related_name="deals")
    buyer_id = fields.ForeignKeyField("models.Users", related_name="bought_deals")
    seller_id = fields.ForeignKeyField("models.Users", related_name="sold_deals")
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharEnumField(enum_type=TransactionCurrencyType)
    status = fields.CharEnumField(enum_type=DealStatus)
    
    is_frozen = fields.BooleanField(default=False)
    support_request = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "deals"