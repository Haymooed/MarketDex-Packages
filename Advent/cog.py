import random
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import Ball, BallInstance, Player, Special
from ballsdex.packages.adventcalendar.models import (
    AdventClaim,
    AdventDayConfig,
    RewardType,
)
from ballsdex.settings import settings


class AdventCalendar(commands.GroupCog, name="advent"):
    """Advent Calendar events for December 1–25."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------------------------------------------------
    # Helper: get today's advent calendar day (1–25)
    # --------------------------------------------------
    async def _get_today_day(self) -> int | None:
        today = datetime.utcnow().date()
        if today.month != 12 or not (1 <= today.day <= 25):
            return None
        return today.day

    # --------------------------------------------------
    # /advent claim
    # --------------------------------------------------
    @app_commands.command(
        name="claim",
        description="Claim today's Advent Calendar reward."
    )
    async def claim(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # ---------------------------------------------
        # Blacklist check
        # ---------------------------------------------
        blacklist_raw = getattr(self.bot, "blacklist", set()) or set()
        blacklist = set()
        for user_id in blacklist_raw:
            try:
                blacklist.add(int(user_id))
            except (TypeError, ValueError):
                pass

        if interaction.user.id in blacklist:
            return await interaction.followup.send(
                "You are blacklisted from using this event.",
                ephemeral=True,
            )

        # ---------------------------------------------
        # Date check
        # ---------------------------------------------
        day = await self._get_today_day()
        if day is None:
            return await interaction.followup.send(
                "The Advent Calendar is only active **December 1–25**.",
                ephemeral=True,
            )

        # ---------------------------------------------
        # Load config for today's reward
        # ---------------------------------------------
        config = (
            await AdventDayConfig.filter(day=day, enabled=True)
            .prefetch_related("ball", "special")
            .first()
        )

        if not config:
            return await interaction.followup.send(
                "There is no active reward configured for today.",
                ephemeral=True,
            )

        # ---------------------------------------------
        # Check if already claimed
        # ---------------------------------------------
        player, _ = await Player.get_or_create(discord_id=interaction.user.id)
        already_claimed = await AdventClaim.filter(player=player, day=day).exists()

        if already_claimed:
            return await interaction.followup.send(
                "You already claimed today's reward.",
                ephemeral=True,
            )

        # ---------------------------------------------
        # Determine reward type
        # ---------------------------------------------
        ball = None
        special = None

        # 🎁 RANDOM SPECIAL
        if config.reward_type == RewardType.RANDOM_SPECIAL:
            enabled_balls = await Ball.filter(enabled=True)
            specials = await Special.all()
            if not enabled_balls or not specials:
                return await interaction.followup.send(
                    "Today's reward is misconfigured. (Missing balls/specials)",
                    ephemeral=True,
                )
            ball = random.choice(enabled_balls)
            special = random.choice(specials)

        # 🎁 SELECTED BALL ONLY
        elif config.reward_type == RewardType.SELECTED_BALL:
            ball = config.ball

        # 🎁 SELECTED BALL + SELECTED SPECIAL
        elif config.reward_type == RewardType.SELECTED_BALL_WITH_SPECIAL:
            ball = config.ball
            special = config.special

        # Safety checks
        if ball is None:
            return await interaction.followup.send(
                "There is no valid reward for today.",
                ephemeral=True,
            )

        if (
            config.reward_type == RewardType.SELECTED_BALL_WITH_SPECIAL
            and special is None
        ):
            return await interaction.followup.send(
                "Today's reward is not configured correctly. (Missing special)",
                ephemeral=True,
            )

        # ---------------------------------------------
        # Create the reward BallInstance
        # ---------------------------------------------
        instance_kwargs = {
            "ball": ball,
            "player": player,
            "server_id": interaction.guild_id,
        }
        if special:
            instance_kwargs["special"] = special

        await BallInstance.create(**instance_kwargs)

        # ---------------------------------------------
        # Save claim entry
        # ---------------------------------------------
        await AdventClaim.create(
            player=player,
            day=day,
            claimed_at=datetime.utcnow(),
        )

        # ---------------------------------------------
        # Build reward message
        # ---------------------------------------------
        emoji = interaction.client.get_emoji(ball.emoji_id) if ball.emoji_id else None
        reward_name = f"{emoji} {ball.country}" if emoji else ball.country

        if special:
            reward_name = f"{reward_name} + **{special.name}**"

        embed = discord.Embed(
            title=f"🎄 Advent Reward – Day {day}",
            description=f"You received: **{reward_name}** {settings.collectible_name}!",
            color=discord.Color.green(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


# --------------------------------------------------
# Setup function for package loading
# --------------------------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(AdventCalendar(bot))
