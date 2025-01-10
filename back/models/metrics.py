from tortoise.models import Model
from tortoise import fields

class Metric(Model):
    uuid = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=100, null=True)

    event_type = fields.CharField(max_length=50)

    timestamp = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "metrics"
