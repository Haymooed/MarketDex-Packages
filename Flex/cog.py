import discord
import tomllib
import os
import json
import time

from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import BallInstance, Player

CONFIG_PATH = "ballsdex/packages/flex/config.toml"
DATA_PATH = "ballsdex/packages/flex/flex_data.json"


def load_data():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_config():
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)["flex"]


async def flex_autocomplete(interaction: discord.Interaction, current: str):
    try:
        player, _ = await Player.get_or_create(discord_id=interaction.user.id)
        balls = await BallInstance.filter(player=player)
    except Exception:
        return []

    current = current.lower()
    choices = []

    for inst in balls:
        ball = inst.countryball
        if not ball:
            continue

        label = (
            f"#{inst.id:0X} {ball.country} "
            f"ATK:{inst.attack_bonus:+d}% HP:{inst.health_bonus:+d}%"
        )

        if current in label.lower():
            choices.append(app_commands.Choice(name=label[:100], value=str(inst.id)))

        if len(choices) >= 25:
            break

    return choices


class Flex(commands.Cog):
    COOLDOWN_SECONDS = 86400

    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @app_commands.command(
        name="flex",
        description="Submit one of your MarketDex items for moderator approval."
    )
    @app_commands.autocomplete(ball=flex_autocomplete)
    async def flex(self, interaction: discord.Interaction, ball: str):
        await interaction.response.defer(ephemeral=True)

        data = load_data()
        uid = str(interaction.user.id)

        last = data.get(uid, {}).get("last_flex", 0)
        now = time.time()

        if now - last < self.COOLDOWN_SECONDS:
            return await interaction.followup.send(
                "Slow down there champ, you can only flex once every 24 hours.",
                ephemeral=True
            )

        try:
            instance_id = int(ball)
        except ValueError:
            return await interaction.followup.send(
                "Invalid selection.",
                ephemeral=True
            )

        try:
            player, _ = await Player.get_or_create(discord_id=interaction.user.id)
            instance = await BallInstance.get(id=instance_id, player=player)
        except Exception:
            return await interaction.followup.send(
                "You don't own that MarketDex ball.",
                ephemeral=True
            )

        mod_channel = self.bot.get_channel(self.config["mod_approval_channel_id"])
        if not mod_channel:
            return await interaction.followup.send(
                "Flex system not configured properly (missing mod channel).",
                ephemeral=True
            )

        buffer = instance.draw_card()
        file = discord.File(buffer, "card.webp")

        emoji = None
        if instance.countryball:
            emoji = interaction.client.get_emoji(instance.countryball.emoji_id)

        name = (
            f"{emoji} {instance.countryball.country}"
            if emoji and instance.countryball else instance.countryball.country
        )

        embed = discord.Embed(
            title="📤 New Flex Submission",
            description=(
                f"From: {interaction.user.mention}\n"
                f"ID: `#{instance.id:0X}`\n"
                f"Name: {name}"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_image(url="attachment://card.webp")

        view = FlexApprovalView(
            bot=self.bot,
            instance_id=instance.id,
            owner_id=interaction.user.id,
            public_channel_id=self.config["public_flex_channel"]
        )
        msg = await mod_channel.send(embed=embed, file=file, view=view)
        view.message = msg

        try:
            await interaction.user.send(
                f"📨 Your flex for `#{instance.id:0X}` has been submitted to moderators!"
            )
        except:
            pass

        data.setdefault(uid, {})["last_flex"] = now
        save_data(data)

        await interaction.followup.send(
            "Your flex has been submitted!",
            ephemeral=True
        )


class FlexDecisionModal(discord.ui.Modal):
    def __init__(self, view, approve):
        super().__init__(title="Approve flex" if approve else "Deny flex")
        self.view_ref = view
        self.approve = approve

        self.notes = discord.ui.TextInput(
            label="Moderator note (optional)",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        instance_id = self.view_ref.instance_id
        owner_id = self.view_ref.owner_id
        public_channel_id = self.view_ref.public_channel_id

        try:
            owner_player, _ = await Player.get_or_create(discord_id=owner_id)
            instance = await BallInstance.get(id=instance_id, player=owner_player)
        except:
            self.view_ref.disable_all()
            if self.view_ref.message:
                await self.view_ref.message.edit(view=self.view_ref)
            return await interaction.followup.send(
                "This ball no longer exists or ownership changed.",
                ephemeral=True
            )

        owner_user = interaction.client.get_user(owner_id)

        if self.approve:
            public_channel = interaction.client.get_channel(public_channel_id)
            if not public_channel:
                return await interaction.followup.send(
                    "Public flex channel not found.",
                    ephemeral=True
                )

            content, file, v = await instance.prepare_for_message(interaction)

            header = (
                "🎉 Flex Approved!\n"
                f"Owner: <@{owner_id}>\n"
            )
            if self.notes.value:
                header += f"Note: {self.notes.value}\n\n"

            await public_channel.send(header + content, file=file, view=v)

            if owner_user:
                try:
                    msg = f"Your flex `#{instance.id:0X}` was approved!"
                    if self.notes.value:
                        msg += f"\nModerator note: {self.notes.value}"
                    await owner_user.send(msg)
                except:
                    pass

            await interaction.followup.send(
                "Flex approved and posted!",
                ephemeral=True
            )

        else:
            if owner_user:
                try:
                    msg = f"Your flex `#{instance.id:0X}` was denied."
                    if self.notes.value:
                        msg += f"\nModerator note: {self.notes.value}"
                    await owner_user.send(msg)
                except:
                    pass

            await interaction.followup.send(
                "Flex denied.",
                ephemeral=True
            )

        self.view_ref.disable_all()
        if self.view_ref.message:
            try:
                await self.view_ref.message.edit(view=self.view_ref)
            except:
                pass


class FlexApprovalView(discord.ui.View):
    def __init__(self, bot, instance_id, owner_id, public_channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.instance_id = instance_id
        self.owner_id = owner_id
        self.public_channel_id = public_channel_id
        self.message = None

    def disable_all(self):
        for child in self.children:
            child.disabled = True

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction, button):
        await interaction.response.send_modal(
            FlexDecisionModal(self, approve=True)
        )

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction, button):
        await interaction.response.send_modal(
            FlexDecisionModal(self, approve=False)
        )
