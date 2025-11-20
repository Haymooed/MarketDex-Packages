import random
import discord
from discord import app_commands
from discord.ext import commands, tasks

from ballsdex.core.models import Ball, Player, BallInstance
from ballsdex.core.utils.utils import is_staff
from ballsdex.settings import settings


class SantaMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.santa_mail_loop.start()

    def cog_unload(self):
        self.santa_mail_loop.cancel()

    async def deliver_santa_mail(self) -> int:
        enabled_balls = await Ball.filter(enabled=True)
        if not enabled_balls:
            return 0

        blacklist_raw = getattr(self.bot, "blacklist", set()) or set()
        blacklist = set()
        for user_id in blacklist_raw:
            try:
                blacklist.add(int(user_id))
            except (TypeError, ValueError):
                continue

        players = await Player.all()
        eligible_players = [player for player in players if player.discord_id not in blacklist]

        if not eligible_players:
            return 0

        chosen_players = random.sample(eligible_players, min(5, len(eligible_players)))
        gifts_sent = 0

        for player in chosen_players:
            ball = random.choice(enabled_balls)
            await BallInstance.create(countryball=ball, player=player)
            await self._send_dm(player.discord_id, ball)
            gifts_sent += 1

        return gifts_sent

    async def _send_dm(self, discord_id: int, ball: Ball) -> None:
        user = self.bot.get_user(discord_id)
        if user is None:
            try:
                user = await self.bot.fetch_user(discord_id)
            except Exception:
                return

        emoji = self.bot.get_emoji(ball.emoji_id) if ball.emoji_id else None
        ball_name = f"{emoji} {ball.country}" if emoji else ball.country

        embed = discord.Embed(
            title="🎅 Santa’s Mail",
            description=(
                "Ho ho ho! You’ve been chosen by Santa! "
                f"You received a {ball_name} {settings.collectible_name}!"
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="Happy holidays from Santa 🎄")

        try:
            await user.send(embed=embed)
        except Exception:
            return

    @tasks.loop(hours=24)
    async def santa_mail_loop(self):
        await self.deliver_santa_mail()

    @santa_mail_loop.before_loop
    async def before_santa_mail_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="santamail", description="Force Santa to deliver gifts right now.")
    @app_commands.check(is_staff())
    async def santamail(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        gifts_sent = await self.deliver_santa_mail()
        await interaction.followup.send(
            f"Santa delivered {gifts_sent} {settings.plural_collectible_name} today.",
            ephemeral=True,
        )
