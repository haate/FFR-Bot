from discord.ext import commands
from .config import config
from . import constants


def is_admin():
    """
    Checks if the user is an admin (from the admin roles in the config)
     or the bot admin
    """

    def predicate(ctx):
        user = ctx.author
        return (
            any(role.id in config.admin_role_ids for role in user.roles)
            or user.id == constants.bot_admin_id
        )

    return commands.check(predicate)


def is_bot_admin():
    """
    Checks if the user is the bot admin.
    """

    def predicate(ctx):
        user = ctx.author
        return user.id == constants.bot_admin_id

    return commands.check(predicate)
