import random

import discord
from discord import app_commands
from discord.ext import commands


FORTUNES = [
    'Luck is on your side—just do not try to catch it with chopsticks!',
    'A shiny pull is in your future. Maybe even today. 👀',
    'Your next trade will be legendary. Or hilarious. Possibly both.',
    'Beware of people offering "free" snacks. They probably want your best ball.',
    'Your luck stat just rolled a natural 20!',
    'Someone nearby is about to ping you with good news.',
    'Collect shinies, but do not forget to collect moments too.',
    'A mysterious traveler will appear with an irresistible offer.',
    'Your favorite ball is secretly cheering you on right now.',
]

CHEERS = [
    'You are absolutely crushing it today!',
    'Keep rolling—your streak is not over yet!',
    'If hype were a stat, you would be max level.',
    'You make the lobby brighter just by showing up.',
    'Confidence check: you passed with flying colors!',
    'Your energy is contagious. Thanks for sharing it!',
    'No crits against you today. Promise.',
]

CONFETTI_MOMENTS = [
    '🎊 A wild celebration appears!',
    '🎉 Confetti cannons primed and ready!',
    '✨ Sparkles acquired. Deploying now...',
    '🥳 The party has entered the chat!',
    '🪩 Mirrorball mode: ON',
]

COLORS = [
    discord.Color.blurple(),
    discord.Color.gold(),
    discord.Color.green(),
    discord.Color.magenta(),
    discord.Color.orange(),
]


@app_commands.guild_only()
class Funhouse(commands.Cog):
    """Lighthearted slash commands for quick celebrations."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='fortune', description='Receive a playful fortune.')
    @app_commands.describe(share='Share publicly instead of sending ephemerally.')
    async def fortune(self, interaction: discord.Interaction, share: bool = False) -> None:
        fortune_text = random.choice(FORTUNES)
        embed = discord.Embed(
            title='Your Fortune',
            description=fortune_text,
            color=random.choice(COLORS),
        )
        embed.set_footer(text='Take it with a grain of glitter ✨')

        await interaction.response.send_message(embed=embed, ephemeral=not share)

    @app_commands.command(name='cheer', description='Send an upbeat cheer to someone (or yourself).')
    @app_commands.describe(user='Who needs a pep talk? Leave blank for yourself.')
    async def cheer(self, interaction: discord.Interaction, user: discord.User | None = None) -> None:
        target = user or interaction.user
        cheer_text = random.choice(CHEERS)
        embed = discord.Embed(
            title='A Cheer Appears!',
            description=f'{target.mention}, {cheer_text}',
            color=random.choice(COLORS),
        )
        embed.set_thumbnail(url=getattr(target.display_avatar, 'url', discord.Embed.Empty))
        embed.set_footer(text='Spread the hype!')

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='confetti', description='Throw a quick celebration into the channel.')
    async def confetti(self, interaction: discord.Interaction) -> None:
        moment = random.choice(CONFETTI_MOMENTS)
        emoji = random.choice(['🎉', '🎊', '✨', '🥳', '🪩', '⭐', '🎈'])
        embed = discord.Embed(description=f"{moment}\n{emoji * 5}", color=random.choice(COLORS))
        embed.set_footer(text='Keep the good vibes rolling!')

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Funhouse(bot))
