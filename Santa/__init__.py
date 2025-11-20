from .cog import SantaMail


async def setup(bot):
    await bot.add_cog(SantaMail(bot))
