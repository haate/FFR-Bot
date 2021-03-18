from discord.ext import commands
from ffrbot.common import constants
import discord
from ffrbot.common import config
from ffrbot.common import text
import logging


# define our checks for the config again since we cannot import checks.py as
# it causes a circular import
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


class ConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @is_bot_admin()
    async def add_admin_roles(self, ctx: commands.Context):
        """
        Adds all pinged roles to the admin roles list
        """
        logging.info("adding to the admins roles list")
        logging.info("old admins:\n" + repr(config.get_admin_role_ids()))
        msg: discord.Message = ctx.message
        new_roles = [x.id for x in msg.role_mentions]
        logging.info("new admin role ids: " + str(new_roles))
        config.set_admin_role_ids(config.get_admin_role_ids().union(new_roles))
        logging.info(
            "new admins:\n"
            + repr([str(x) for x in config.get_admin_role_ids()])
        )
        channel: discord.TextChannel = ctx.channel
        guild: discord.Guild = ctx.guild
        send_msg = "admins:\n" + ", ".join(
            [
                guild.get_role(int(x)).mention
                for x in config.get_admin_role_ids()
            ]
        )
        await channel.send(send_msg)

    @commands.command()
    @is_bot_admin()
    async def remove_admin_roles(self, ctx: commands.Context):
        """
        Removes all pinged roles from the admin roles list
        """
        logging.info("removing from the admins roles list")
        logging.info("old admins:\n" + repr(config.get_admin_role_ids()))
        msg: discord.Message = ctx.message
        remove_roles = [str(x.id) for x in msg.role_mentions]
        config.set_admin_role_ids(
            config.get_admin_role_ids() - set(remove_roles)
        )
        logging.info("new admins:\n" + repr(config.get_admin_role_ids()))
        channel: discord.TextChannel = ctx.channel
        guild: discord.Guild = ctx.guild
        send_msg = "admins:\n" + ", ".join(
            [
                guild.get_role(int(x)).mention
                for x in config.get_admin_role_ids()
            ]
        )
        await channel.send(send_msg)

    @is_admin()
    @commands.command()
    async def list_admin_roles(self, ctx: commands.Context):
        """
        List all current roles on the admin roles list
        """
        channel: discord.TextChannel = ctx.channel
        guild: discord.Guild = ctx.guild
        msg = "admins:\n" + ", ".join(
            [
                guild.get_role(int(x)).mention
                for x in config.get_admin_role_ids()
            ]
        )
        await channel.send(msg)

    @commands.command()
    async def set_polls_category(self, ctx: commands.Context):
        """
        Sets the polls category to the category of the current channel
        """

        category: discord.CategoryChannel = ctx.channel.category
        if category is None:
            ctx.channel.send(text.category_not_found)
            return

        config.set_polls_category_id(category.id)

    @commands.command()
    @is_admin()
    async def set_race_org_channel(self, ctx: commands.Context):
        """
        Sets the current channel as the race organization channel

        All (sync and async) races must be started from this channel
        """
        logging.info(
            "setting the race organization channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )

        config.set_race_org_channel_id(ctx.channel.id)

    @commands.command()
    @is_admin()
    async def set_race_results_channel(self, ctx: commands.Context):
        """
        Sets the current channel as the race results channel

        All (sync and async) race results will be posted here
        """
        logging.info(
            "setting the race results channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )
        config.set_race_results_channel_id(ctx.channel.id)

    @commands.command()
    @is_admin()
    async def set_role_requests_channel(self, ctx: commands.Context):
        """
        Sets the current channel as the role requests channel

        All role related commands will need to be run here
        """

        logging.info(
            "setting the role requests channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )
        config.set_role_requests_channel_id(ctx.channel.id)
