from .cog import SantaMail

__all__ = ["SantaMail"]


async def setup(bot):
    await bot.add_cog(SantaMail(bot))
