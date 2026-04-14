from typing import TYPE_CHECKING

from .cog import Collectibles
from .admin import collectibles

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    await bot.add_cog(Collectibles(bot))
    admin_cog = bot.cogs.get("Admin")
    if admin_cog is not None and hasattr(admin_cog, "admin"):
        admin_cog.admin.add_command(collectibles)
