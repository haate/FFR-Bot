from discord.ext import commands
import discord
from typing import *
from ..common import config, text, constants, checks
import logging


class ConfigCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    @checks.is_bot_admin()
    @commands.guild_only()
    async def add_admin_roles(self, ctx: commands.Context) -> None:
        """
        Adds all pinged roles to the admin roles list
        """
        guild = cast(discord.Guild, ctx.guild)
        logging.info("adding to the admins roles list")
        logging.info(
            "old admins:\n" + repr(config.get_admin_role_ids(guild.id))
        )
        msg: discord.Message = ctx.message
        new_roles = [x.id for x in msg.role_mentions]
        logging.info("new admin role ids: " + str(new_roles))
        config.add_admin_role_ids(
            guild.id,
            new_roles,
        )
        channel = cast(discord.TextChannel, ctx.channel)
        send_msg = "admins:\n" + ", ".join(
            [
                role.mention
                for role in (
                    cast(discord.Role, guild.get_role(x))
                    for x in config.get_admin_role_ids(guild.id)
                    if guild.get_role(x) is not None
                )
            ]
        )
        await channel.send(send_msg)

    @commands.command()
    @checks.is_bot_admin()
    @commands.guild_only()
    async def remove_admin_roles(self, ctx: commands.Context) -> None:
        """
        Removes all pinged roles from the admin roles list
        """
        guild = cast(discord.Guild, ctx.guild)
        logging.info("removing from the admins roles list")
        logging.info(
            "old admins:\n" + repr(config.get_admin_role_ids(guild.id))
        )
        msg: discord.Message = ctx.message
        remove_roles = [x.id for x in msg.role_mentions]
        config.remove_admin_role_ids(guild.id, remove_roles)
        new_admin_ids = config.get_admin_role_ids(guild.id)
        logging.info("new admins:\n" + repr(new_admin_ids))
        channel = cast(discord.TextChannel, ctx.channel)
        send_msg = "admins:\n" + ", ".join(
            [
                role.mention
                for role in (
                    cast(discord.Role, guild.get_role(x))
                    for x in new_admin_ids
                    if guild.get_role(x) is not None
                )
            ]
        )
        await channel.send(send_msg)

    @checks.is_admin()
    @commands.command()
    @commands.guild_only()
    async def list_admin_roles(self, ctx: commands.Context) -> None:
        """
        List all current roles on the admin roles list
        """
        channel = cast(discord.TextChannel, ctx.channel)
        guild = cast(discord.Guild, ctx.guild)
        msg = "admins:\n" + ", ".join(
            [
                role.mention
                for role in (
                    cast(discord.Role, guild.get_role(x))
                    for x in config.get_admin_role_ids()
                    if guild.get_role(x) is not None
                )
            ]
        )
        await channel.send(msg)

    @commands.command()
    @commands.guild_only()
    async def set_polls_category(self, ctx: commands.Context) -> None:
        """
        Sets the polls category to the category of the current channel
        """

        category = cast(discord.TextChannel, ctx.channel).category
        if category is None:
            await ctx.channel.send(text.category_not_found)
        else:
            config.set_polls_category_id(category.id)

    @commands.command()
    @checks.is_admin()
    @commands.guild_only()
    async def set_race_org_channel(self, ctx: commands.Context) -> None:
        """
        Sets the current channel as the race organization channel

        All (sync and async) races must be started from this channel
        """

        assert isinstance(ctx.channel, discord.TextChannel)

        logging.info(
            "setting the race organization channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )

        config.set_race_org_channel_id(ctx.channel.id)

    @commands.command()
    @checks.is_admin()
    @commands.guild_only()
    async def set_race_results_channel(self, ctx: commands.Context) -> None:
        """
        Sets the current channel as the race results channel

        All (sync and async) race results will be posted here
        """

        assert isinstance(ctx.channel, discord.TextChannel)

        logging.info(
            "setting the race results channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )
        config.set_race_results_channel_id(ctx.channel.id)

    @commands.command()
    @checks.is_admin()
    @commands.guild_only()
    async def set_role_requests_channel(self, ctx: commands.Context) -> None:
        """
        Sets the current channel as the role requests channel

        All role related commands will need to be run here
        """

        assert isinstance(ctx.channel, discord.TextChannel)

        logging.info(
            "setting the role requests channel, "
            + "channel name: "
            + ctx.channel.name
            + ", channel id: "
            + str(ctx.channel.id)
        )
        config.set_role_requests_channel_id(ctx.channel.id)
