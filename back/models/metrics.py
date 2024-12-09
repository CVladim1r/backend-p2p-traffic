from tortoise.models import Model
from tortoise import fields

class Metric(Model):
    id = fields.IntField(pk=True)
    event_type = fields.CharField(max_length=50)
    timestamp = fields.DatetimeField(auto_now_add=True)
    user_id = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "metrics"
