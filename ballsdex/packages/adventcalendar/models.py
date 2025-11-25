from enum import Enum

from tortoise import fields, models


class RewardType(str, Enum):
    RANDOM_SPECIAL = "random_special"
    SELECTED_BALL = "selected_ball"
    SELECTED_BALL_WITH_SPECIAL = "selected_ball_with_special"


class AdventDayConfig(models.Model):
    id = fields.IntField(pk=True)
    day = fields.IntField()
    enabled = fields.BooleanField(default=True)
    reward_type = fields.CharField(max_length=48)
    ball = fields.ForeignKeyField(
        "core.Ball", related_name="advent_day_configs", null=True, on_delete=fields.SET_NULL
    )
    special = fields.ForeignKeyField(
        "core.Special",
        related_name="advent_day_configs",
        null=True,
        on_delete=fields.SET_NULL,
    )
    description = fields.TextField(null=True)

    class Meta:
        table = "advent_day_config"
        unique_together = ("day",)


class AdventClaim(models.Model):
    id = fields.IntField(pk=True)
    player = fields.ForeignKeyField("core.Player", related_name="advent_claims")
    day = fields.IntField()
    claimed_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "advent_claim"
        unique_together = ("player", "day")
