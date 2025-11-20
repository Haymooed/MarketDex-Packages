from __future__ import annotations

import random
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import Ball, BallInstance, Player

AUS_TZ = ZoneInfo("Australia/Sydney")


@app_commands.guild_only()
class SantaMail(commands.GroupCog, group_name="santa"):
    """Send a surprise ball to a random member in Australian time."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="mail", description="Deliver a random Tier 1-100 ball to someone via Santa mail.")
    async def mail(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        assert guild is not None

        if not guild.chunked:
            await guild.chunk()

        candidates = [member for member in guild.members if not member.bot]
        if not candidates:
            await interaction.followup.send("No eligible members found.", ephemeral=True)
            return

        recipient = random.choice(candidates)

        eligible_balls = await Ball.filter(enabled=True, rarity__gte=1, rarity__lte=100)
        if not eligible_balls:
            await interaction.followup.send(
                "No available Tier 1-100 balls to deliver.", ephemeral=True
            )
            return

        ball = random.choice(eligible_balls)
        player, _ = await Player.get_or_create(discord_id=recipient.id)
        instance = await BallInstance.create(player=player, ball=ball)

        emoji = self.bot.get_emoji(getattr(ball, "emoji_id", None))
        ball_name = getattr(ball, "country", getattr(ball, "name", "Unknown"))
        ball_label = f"{emoji} {ball_name}" if emoji else ball_name

        image_url = (
            getattr(ball, "spawn_image", None)
            or getattr(ball, "spawn_image_url", None)
            or getattr(ball, "image_url", None)
            or getattr(ball, "image", None)
            or getattr(ball, "card_url", None)
        )

        now = datetime.now(AUS_TZ)
        embed = discord.Embed(
            title="🎅 Santa Mail!",
            description=(
                "Santa has chosen you for a surprise delivery!\n"
                f"You received **{ball_label}** (ID `#{instance.id:0X}`)"
            ),
            color=discord.Color.red(),
            timestamp=now,
        )
        embed.add_field(
            name="Sydney Time",
            value=now.strftime("%d %b %Y, %I:%M %p AEST/AEDT"),
            inline=False,
        )
        embed.set_footer(text="Tier pool: T1-T100 | Delivered with holiday cheer")
        if image_url:
            embed.set_image(url=image_url)

        delivered = True
        try:
            await recipient.send(embed=embed)
        except discord.Forbidden:
            delivered = False

        summary = (
            f"🎁 {'Delivered' if delivered else 'Could not deliver'} {ball_label} "
            f"(ID `#{instance.id:0X}`) to {recipient.mention}."
        )

        await interaction.followup.send(summary, ephemeral=True)

