from .cog import Funhouse

async def setup(bot):
    await bot.add_cog(Funhouse(bot))
