import discord
import random
import tomllib
import os
import json
import time

from discord import app_commands
from discord.ext import commands
from ballsdex.core.models import Ball, balls, Player, BallInstance

CONFIG_PATH = "ballsdex/packages/merchant/config.toml"
DATA_PATH = "ballsdex/packages/merchant/merchant_data.json"


def load_config():
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def load_data():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


class BuyButton(discord.ui.Button):
    def __init__(self, merchant_cog, ball, price, currency):
        super().__init__(label=f"Buy {ball.country}", style=discord.ButtonStyle.green)
        self.merchant_cog = merchant_cog
        self.ball = ball
        self.price = price
        self.currency = currency

    async def callback(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)

        user_data = data.setdefault(uid, {"balance": 0, "last_claim": 0, "purchased_ids": []})

        if self.ball.id in user_data["purchased_ids"]:
            return await interaction.response.send_message(
                "You've already bought this ball during this shop rotation.",
                ephemeral=True
            )

        if user_data["balance"] < self.price:
            return await interaction.response.send_message(
                f"❌ You need **{self.price - user_data['balance']}** more {self.currency}!",
                ephemeral=True
            )

        user_data["balance"] -= self.price
        user_data["purchased_ids"].append(self.ball.id)
        save_data(data)

        player, _ = await Player.get_or_create(discord_id=interaction.user.id)
        instance = await BallInstance.create(
            ball_id=self.ball.id,
            player=player
        )

        emoji = interaction.client.get_emoji(self.ball.emoji_id)
        e = emoji if emoji else "🎁"

        await interaction.response.send_message(
            f"{e} {interaction.user.mention} bought **{self.ball.country}** "
            f"(ID `#{instance.id:0X}`)!"
        )

        log_id = self.merchant_cog.config.get("transaction_log_channel")
        if log_id:
            channel = interaction.client.get_channel(log_id)
            if channel:
                await channel.send(
                    f"🧾 **Purchase Log**\n"
                    f"User: {interaction.user.mention}\n"
                    f"Item: {self.ball.country}\n"
                    f"Instance ID: `#{instance.id:0X}`\n"
                    f"Cost: {self.price} {self.currency}"
                )


class Merchant(commands.GroupCog, group_name="merchant"):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.shop_items = []
        self.last_refresh = 0
        self.refresh_shop()

    def refresh_shop(self):
        min_rarity = self.config.get("min_rarity", 1)
        max_rarity = self.config.get("max_rarity", 200)

        data = load_data()
        for uid in data:
            data[uid]["purchased_ids"] = []
        save_data(data)

        available = [
            b for b in balls.values()
            if b.enabled
            and b.rarity is not None
            and b.rarity >= 1
            and min_rarity <= b.rarity <= max_rarity
        ]

        if not available:
            self.shop_items = []
            return

        weights = [max(1, int(b.rarity)) for b in available]

        self.shop_items = random.choices(
            available,
            weights=weights,
            k=min(5, len(available))
        )

        self.last_refresh = time.time()

    @app_commands.command(name="view", description="View today's merchant stock.")
    async def view(self, interaction: discord.Interaction):
        currency = self.config.get("currency_name", "Market Tokens")

        if time.time() - self.last_refresh > 86400:
            self.refresh_shop()

        remaining = int(86400 - (time.time() - self.last_refresh))
        hours = max(0, remaining // 3600)
        mins = max(0, (remaining % 3600) // 60)

        embed = discord.Embed(
            title="🛍️ Merchant’s Market",
            description=f"Spend your {currency} on exclusive items.\n"
                        f"Restocks in **{hours}h {mins}m**.",
            color=discord.Color.gold()
        )

        view = discord.ui.View()

        for ball in self.shop_items:
            rarity = max(1, int(ball.rarity))

            max_rarity = 200
            min_rarity = 1
            max_price = 50
            min_price = 5

            price = int(
                min_price
                + (max_rarity - rarity) * (max_price - min_price)
                / (max_rarity - min_rarity)
            )
            price = max(price, min_price)

            emoji = interaction.client.get_emoji(ball.emoji_id)
            name = f"{emoji} {ball.country}" if emoji else ball.country

            embed.add_field(
                name=name,
                value=f"Rarity: {ball.rarity}\nCost: **{price} {currency}**",
                inline=False,
            )

            view.add_item(BuyButton(self, ball, price, currency))

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="refresh", description="Force-refresh the merchant stock.")
    async def refresh(self, interaction: discord.Interaction):
        roles = self.config.get("admin_roles", [])

        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("Not in a guild.", ephemeral=True)

        if not any(r.id in roles for r in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        self.refresh_shop()
        await interaction.response.send_message("🔄 Merchant stock refreshed!")

    @app_commands.command(name="balance", description="Check your Market Token balance.")
    async def balance(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)
        currency = self.config.get("currency_name", "Market Tokens")
        user_data = data.get(uid, {"balance": 0, "last_claim": 0})
        bal = user_data["balance"]

        now = time.time()
        left = max(0, 86400 - (now - user_data["last_claim"]))

        if left > 0:
            h = left // 3600
            m = (left % 3600) // 60
            cd = f"Next daily in {h}h {m}m"
        else:
            cd = "Daily available."

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Wallet",
            description=f"💰 **{bal} {currency}**\n{cd}",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim daily Market Tokens.")
    async def daily(self, interaction: discord.Interaction):
        data = load_data()
        uid = str(interaction.user.id)
        currency = self.config.get("currency_name", "Market Tokens")
        now = time.time()

        user = data.setdefault(uid, {"balance": 0, "last_claim": 0, "purchased_ids": []})

        if now - user["last_claim"] < 86400:
            left = int(86400 - (now - user["last_claim"]))
            h = left // 3600
            m = (left % 3600) // 60
            return await interaction.response.send_message(
                f"🕓 Claim again in {h}h {m}m.",
                ephemeral=True
            )

        reward = random.randint(3, 10)
        user["balance"] += reward
        user["last_claim"] = now
        save_data(data)

        await interaction.response.send_message(
            f"🎁 You claimed **{reward} {currency}**!"
        )

    @app_commands.command(name="give", description="Give Market Tokens.")
    async def give(self, interaction: discord.Interaction, user: discord.User, amount: int):
        roles = self.config.get("admin_roles", [])
        currency = self.config.get("currency_name", "Market Tokens")

        if not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("Not in a guild.")

        if not any(r.id in roles for r in interaction.user.roles):
            return await interaction.response.send_message("No permission.", ephemeral=True)

        data = load_data()
        uid = str(user.id)
        db = data.setdefault(uid, {"balance": 0, "last_claim": 0, "purchased_ids": []})
        db["balance"] += amount
        save_data(data)

        await interaction.response.send_message(
            f"Gave **{amount} {currency}** to {user.mention}."
        )

        try:
            await user.send(f"You received **{amount} {currency}**.")
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(Merchant(bot))
