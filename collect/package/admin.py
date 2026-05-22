from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from asgiref.sync import sync_to_async

from ballsdex.core.utils import checks
from bd_models.models import Player
from collect.models import Collectible, PlayerCollectible, GroupName

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.admin.collectibles")

GROUP_NAME = "collectible"
GROUP_NAME_CAP = GROUP_NAME.capitalize()
plural = "collectibles"


class CollectibleConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, value: str) -> Collectible:
        try:
            return await sync_to_async(Collectible.objects.get)(pk=int(value))
        except Exception:
            pass

        try:
            return await sync_to_async(Collectible.objects.get)(name__iexact=value)
        except Exception:
            pass

        result = await sync_to_async(
            lambda: Collectible.objects.filter(name__icontains=value).first()
        )()

        if result is None:
            raise commands.BadArgument(f'{GROUP_NAME_CAP[:-1]} "{value}" not found.')

        return result


class CollectAdmin(commands.Cog):
    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.group_model: GroupName | None = None
        self.collectibles = None

    async def cog_load(self):
        global GROUP_NAME, GROUP_NAME_CAP, plural

        try:
            self.group_model = await GroupName.objects.aget(pk=1)
        except GroupName.DoesNotExist:
            self.group_model = await GroupName.objects.acreate(
                group_name="collectible",
                plural="collectibles",
            )

        GROUP_NAME = self.group_model.group_name
        GROUP_NAME_CAP = GROUP_NAME.capitalize()
        plural = self.group_model.plural

        self.collectibles = commands.hybrid_group(
            name=plural.lower(),
            description=f"{GROUP_NAME_CAP} management commands",
            fallback=None,
        )(self._collectibles_root)

    async def _collectibles_root(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand.", ephemeral=True)

    @checks.is_staff()
    @commands.hybrid_command(name="admin_give")
    async def collectibles_give(
        self,
        ctx: commands.Context,
        user: discord.User,
        collectible: str,
    ):
        if ctx.command.parent is None:
            return

        try:
            collectible_obj = await CollectibleConverter().convert(ctx, collectible)
        except commands.BadArgument as e:
            await ctx.send(str(e), ephemeral=True)
            return

        player, _ = await sync_to_async(Player.objects.get_or_create)(
            discord_id=user.id
        )

        exists = await sync_to_async(
            PlayerCollectible.objects.filter(
                player=player,
                collectible=collectible_obj,
            ).exists
        )()

        if exists:
            await ctx.send(
                f"{user.mention} already owns **{collectible_obj.name}**.",
                ephemeral=True,
            )
            return

        await sync_to_async(PlayerCollectible.objects.create)(
            player=player,
            collectible=collectible_obj,
        )

        await ctx.send(
            f"Gave **{collectible_obj.name}** to {user.mention}. Reload the cache.",
            ephemeral=True,
        )

        log.info(
            f"{ctx.author} ({ctx.author.id}) gave '{collectible_obj.name}' to {user} ({user.id})",
            extra={"webhook": True},
        )

    @checks.is_staff()
    @commands.hybrid_command(name="admin_remove")
    async def collectibles_remove(
        self,
        ctx: commands.Context,
        user: discord.User,
        collectible: str,
    ):
        if ctx.command.parent is None:
            return

        try:
            collectible_obj = await CollectibleConverter().convert(ctx, collectible)
        except commands.BadArgument as e:
            await ctx.send(str(e), ephemeral=True)
            return

        try:
            player = await sync_to_async(Player.objects.get)(discord_id=user.id)
            owned = await sync_to_async(PlayerCollectible.objects.get)(
                player=player,
                collectible=collectible_obj,
            )
        except Exception:
            await ctx.send(
                f"{user.mention} does not own **{collectible_obj.name}**.",
                ephemeral=True,
            )
            return

        await sync_to_async(owned.delete)()

        await ctx.send(
            f"Removed **{collectible_obj.name}** from {user.mention}. Reload the cache.",
            ephemeral=True,
        )

        log.info(
            f"{ctx.author} ({ctx.author.id}) removed '{collectible_obj.name}' from {user} ({user.id})",
            extra={"webhook": True},
        )

    @checks.is_staff()
    @commands.hybrid_command(name="admin_create")
    async def collectibles_create(
        self,
        ctx: commands.Context,
        name: str,
        emoji: str,
        cost: int,
        image_url: str,
        requirement_type: str | None = None,
        requirement_value: str | None = None,
    ):
        if ctx.command.parent is None:
            return

        exists = await sync_to_async(
            Collectible.objects.filter(name__iexact=name).exists
        )()

        if exists:
            await ctx.send(
                f"A {GROUP_NAME[:-1]} with that name already exists.",
                ephemeral=True,
            )
            return

        collectible = await sync_to_async(Collectible.objects.create)(
            name=name,
            emoji=emoji,
            cost=cost,
            image_url=image_url,
            requirement_type=requirement_type,
            requirement_value=requirement_value,
        )

        await ctx.send(
            f"Created **{collectible.name}**.\nReload the bot's cache.\n{collectible.image_url}",
            ephemeral=True,
        )

        log.info(
            f"{ctx.author} ({ctx.author.id}) created collectible '{collectible.name}'",
            extra={"webhook": True},
        )
