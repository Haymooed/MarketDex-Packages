import discord
import tomllib

from discord import app_commands
from discord.ext import commands

from ballsdex.core.models import BallInstance, Player


CONFIG_PATH = "ballsdex/packages/flex/config.toml"


def load_config():
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)["flex"]


class Flex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @app_commands.command(name="flex", description="Submit one of your balls for flex approval.")
    async def flex(self, interaction: discord.Interaction, ball_id: str):
        raw = ball_id.strip()
        if raw.startswith("#"):
            raw = raw[1:]

        try:
            instance_id = int(raw, 16)
        except ValueError:
            await interaction.response.send_message(
                "That doesn't look like a valid ball ID. Use the hex ID like `#ABC123`.",
                ephemeral=True,
            )
            return

        try:
            player, _ = await Player.get_or_create(discord_id=interaction.user.id)
            instance = await BallInstance.get(id=instance_id, player=player)
        except Exception:
            await interaction.response.send_message(
                "I couldn't find a ball with that ID that you own.",
                ephemeral=True,
            )
            return

        mod_channel = self.bot.get_channel(self.config["mod_approval_channel_id"])
        if not mod_channel:
            await interaction.response.send_message(
                "Flex system is not configured correctly (mod channel missing).",
                ephemeral=True,
            )
            return

        buffer = instance.draw_card()
        file = discord.File(buffer, "card.webp")

        emoji = None
        if instance.countryball and hasattr(instance.countryball, "emoji_id"):
            emoji = interaction.client.get_emoji(instance.countryball.emoji_id)

        name = (
            f"{emoji} {instance.countryball.country}"
            if emoji and instance.countryball
            else (
                instance.countryball.country
                if instance.countryball
                else f"Ball #{instance.id:0X}"
            )
        )

        embed = discord.Embed(
            title="New Flex Submission",
            description=(
                f"From: {interaction.user.mention}\n"
                f"ID: `#{instance.id:0X}`\n"
                f"Ball: {name}"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_image(url="attachment://card.webp")

        view = FlexApprovalView(
            bot=self.bot,
            instance_id=instance.id,
            owner_id=interaction.user.id,
            public_channel_id=self.config["public_flex_channel"],
        )

        msg = await mod_channel.send(embed=embed, file=file, view=view)
        view.message = msg

        try:
            await interaction.user.send(
                f"Your flex submission for `#{instance.id:0X}` has been sent to moderators for review."
            )
        except discord.Forbidden:
            pass

        await interaction.response.send_message(
            "Your flex has been sent for approval.",
            ephemeral=True,
        )


class FlexDecisionModal(discord.ui.Modal):
    def __init__(self, view: "FlexApprovalView", approve: bool):
        title = "Approve flex" if approve else "Deny flex"
        super().__init__(title=title)
        self.view_ref = view
        self.approve = approve
        self.notes = discord.ui.TextInput(
            label="Moderator note (optional)",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500,
        )
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        instance_id = self.view_ref.instance_id
        owner_id = self.view_ref.owner_id
        public_channel_id = self.view_ref.public_channel_id

        try:
            owner_player, _ = await Player.get_or_create(discord_id=owner_id)
            instance = await BallInstance.get(id=instance_id, player=owner_player)
        except Exception:
            await interaction.response.send_message(
                "This flex entry is no longer valid (ball not found or ownership changed).",
                ephemeral=True,
            )
            self.view_ref.disable_all()
            if self.view_ref.message:
                try:
                    await self.view_ref.message.edit(view=self.view_ref)
                except discord.HTTPException:
                    pass
            return

        owner_user = interaction.client.get_user(owner_id)

        if self.approve:
            public_channel = interaction.client.get_channel(public_channel_id)
            if not public_channel:
                await interaction.response.send_message(
                    "Public flex channel not found.",
                    ephemeral=True,
                )
                return

            content, file, card_view = await instance.prepare_for_message(interaction)

            header = (
                f"✅ Flex approved by {interaction.user.mention}!\n"
                f"Owner: <@{owner_id}>\n"
            )
            if self.notes.value:
                header += f"Moderator note: {self.notes.value}\n\n"

            await public_channel.send(content=header + content, file=file, view=card_view)

            await interaction.response.send_message(
                "Flex approved and posted.",
                ephemeral=True,
            )

            if owner_user:
                try:
                    msg = f"✅ Your flex for `#{instance.id:0X}` was approved by {interaction.user}."
                    if self.notes.value:
                        msg += f"\nModerator note: {self.notes.value}"
                    await owner_user.send(msg)
                except discord.Forbidden:
                    pass
        else:
            await interaction.response.send_message(
                "Flex denied.",
                ephemeral=True,
            )

            if owner_user:
                try:
                    msg = f"❌ Your flex for `#{instance.id:0X}` was denied by {interaction.user}."
                    if self.notes.value:
                        msg += f"\nModerator note: {self.notes.value}"
                    await owner_user.send(msg)
                except discord.Forbidden:
                    pass

        self.view_ref.disable_all()
        if self.view_ref.message:
            try:
                await self.view_ref.message.edit(view=self.view_ref)
            except discord.HTTPException:
                pass


class FlexApprovalView(discord.ui.View):
    def __init__(self, bot, instance_id: int, owner_id: int, public_channel_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.instance_id = instance_id
        self.owner_id = owner_id
        self.public_channel_id = public_channel_id
        self.message: discord.Message | None = None

    def disable_all(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    async def on_timeout(self):
        self.disable_all()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FlexDecisionModal(self, approve=True)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FlexDecisionModal(self, approve=False)
        await interaction.response.send_modal(modal)
