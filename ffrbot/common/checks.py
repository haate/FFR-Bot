from discord.ext import commands
import discord
from . import config, constants
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands.core import _CheckDecorator


def is_admin() -> _CheckDecorator:
    """
    Checks if the user is an admin (from the admin roles in the config)
     or the bot admin
    """

    async def predicate(ctx: commands.Context) -> bool:
        user = ctx.author
        return (
            isinstance(user, discord.Member)
            and any(
                role.id in config.get_admin_role_ids() for role in user.roles
            )
        ) or user.id == constants.BOT_ADMIN_ID

    return commands.check(predicate)


def is_bot_admin() -> _CheckDecorator:
    """
    Checks if the user is the bot admin.
    """

    async def predicate(ctx: commands.Context) -> bool:
        user = ctx.author
        return user.id == constants.BOT_ADMIN_ID

    return commands.check(predicate)


def is_role_requests_channel() -> _CheckDecorator:
    """
    Checks if the channel the command was executed in is the role requests
    channel.
    """

    async def predicate(ctx: commands.Context) -> bool:
        return ctx.channel.id == config.get_role_requests_channel_id()

    return commands.check(predicate)
