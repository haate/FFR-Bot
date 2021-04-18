from discord.ext import commands
import discord
from . import config, constants
from typing import *

RT = TypeVar("RT")  # return type


def is_admin() -> Callable[..., RT]:
    """
    Checks if the user is an admin (from the admin roles in the config)
     or the bot admin
    """

    async def predicate(ctx: commands.Context) -> bool:
        user = ctx.author
        guild = ctx.guild

        if user.id == constants.BOT_ADMIN_ID:
            return True

        if guild is None or not isinstance(user, discord.Member):
            return False

        assert isinstance(ctx.guild, discord.Guild)
        admin_role_ids = config.guild.get_admin_role_ids(ctx.guild.id) or []

        return any(role.id in admin_role_ids for role in user.roles)

    return commands.check(predicate)


def is_bot_admin() -> Callable[..., RT]:

    """
    Checks if the user is the bot admin.
    """

    async def predicate(ctx: commands.Context) -> bool:
        user = ctx.author
        return user.id == constants.BOT_ADMIN_ID

    return commands.check(predicate)


def is_role_requests_channel() -> Callable[..., RT]:

    """
    Checks if the channel the command was executed in is the role requests
    channel.
    """

    async def predicate(ctx: commands.Context) -> bool:
        guild = ctx.guild
        guild_id = guild.id if guild is not None else -1

        return ctx.channel.id == config.guild.get_role_requests_channel_id(
            guild_id
        )

    return commands.check(predicate)
