from discord.ext import commands
from . import config, constants


def is_admin():
    """
    Checks if the user is an admin (from the admin roles in the config)
     or the bot admin
    """

    def predicate(ctx):
        user = ctx.author
        return (
            any(role.id in config.get_admin_role_ids() for role in user.roles)
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


def is_role_requests_channel():
    """
    Checks if the channel the command was executed in is the role requests
    channel.
    """

    def predicate(ctx):
        return ctx.channel.id == config.get_role_requests_channel_id()

    return commands.check(predicate)
