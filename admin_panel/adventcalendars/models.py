from django.db import models
from django.utils.translation import gettext_lazy as _


class RewardType(models.TextChoices):
    RANDOM_SPECIAL = "random_special", _("Random special")
    SELECTED_BALL = "selected_ball", _("Selected ball")
    SELECTED_BALL_WITH_SPECIAL = "selected_ball_with_special", _("Selected ball with special")


class AdventDayConfig(models.Model):
    day = models.PositiveSmallIntegerField()
    enabled = models.BooleanField(default=True)
    reward_type = models.CharField(max_length=48, choices=RewardType.choices)
    ball = models.ForeignKey(
        "core.Ball", related_name="advent_day_configs", on_delete=models.SET_NULL, null=True
    )
    special = models.ForeignKey(
        "core.Special", related_name="advent_day_configs", on_delete=models.SET_NULL, null=True
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "advent_day_config"
        unique_together = ("day",)
        verbose_name = "Advent day configuration"
        verbose_name_plural = "Advent day configurations"

    def __str__(self) -> str:
        label = f"Day {self.day}"
        if self.description:
            label = f"{label} – {self.description[:40]}"
        return label


class AdventClaim(models.Model):
    player = models.ForeignKey("core.Player", related_name="advent_claims", on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField()
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "advent_claim"
        unique_together = ("player", "day")
        verbose_name = "Advent claim"
        verbose_name_plural = "Advent claims"

    def __str__(self) -> str:
        return f"{self.player_id} – Day {self.day}"
