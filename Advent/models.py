from tortoise import fields, models
from enum import IntEnum


class RewardType(IntEnum):
    RANDOM_SPECIAL = 1
    SELECTED_BALL = 2
    SELECTED_BALL_WITH_SPECIAL = 3


class AdventDayConfig(models.Model):
    """
    Stores which reward is available on each day (Dec 1–25).
    """
    id = fields.IntField(pk=True)

    day = fields.IntField()  # 1–25
    enabled = fields.BooleanField(default=True)

    reward_type = fields.IntEnumField(RewardType)

    ball = fields.ForeignKeyField(
        "models.Ball",
        null=True,
        related_name="advent_reward_ball",
    )

    special = fields.ForeignKeyField(
        "models.Special",
        null=True,
        related_name="advent_reward_special",
    )

    class Meta:
        table = "adventdayconfig"


class AdventClaim(models.Model):
    """
    Stores which user has claimed which day.
    Prevents re-claiming.
    """
    id = fields.IntField(pk=True)

    player = fields.ForeignKeyField(
        "models.Player",
        related_name="advent_claims"
    )

    day = fields.IntField()  # 1–25
    claimed_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "adventclaim"
        unique_together = ("player", "day")
