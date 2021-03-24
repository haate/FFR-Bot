from ..common import constants, checks, config, snippits
from ..common.redis_client import RedisClient

from discord.ext import commands
from typing import *
import discord

import logging


class Core(commands.Cog):
    """
    Core bot commands
    """

    def __init__(self, bot: commands.Bot, db: RedisClient):
        self.bot: commands.Bot = bot
        self.db: RedisClient = db

    @commands.command()
    @commands.guild_only()
    @checks.is_bot_admin()
    async def init_guild(self, ctx: commands.Context) -> None:
        """
        Sets the guild (internal name for discord servers) that the bot will be
        used in.
        """
        logging.info("initializing bot in guild.")
        guild: discord.Guild = cast(discord.Guild, ctx.guild)

        async def yes() -> None:

            config.set_guild_id(guild.id)
            logging.info("Guild set to: " + guild.name)

        async def no() -> None:
            logging.info("Guild not set.")

        if config.get_guild() is None:
            await yes()
        else:
            await snippits.wait_for_yes_no(
                self.bot,
                ctx,
                f"Guild already set to {guild.name} with owner: {guild.owner},"
                f" are you sure you want to overwrite it?",
                yes,
                no,
            )

    @commands.command()
    @checks.is_bot_admin()
    async def purge(self, ctx: commands.Context) -> None:
        """
        Clears the channel history -- for testing
        """

        async def yes() -> None:
            channel = ctx.channel
            if isinstance(channel, discord.TextChannel):
                await channel.purge(limit=100000)

        await snippits.wait_for_yes_no(
            self.bot,
            ctx,
            "Are you sure you want to delete this channel's message"
            " history entirely? This is not revertible",
            yes,
        )

    @commands.command(aliases=["whoami"])
    async def who_am_i(self, ctx: commands.Context) -> None:
        """
        Messages you your discord user id
        """
        await ctx.author.send(ctx.author.id)
        await ctx.message.delete()

    @commands.command()
    async def version(self, ctx: commands.Context) -> None:
        """
        Messages you the version of the bot
        """
        await ctx.author.send(
            f"version: {constants.VERSION}\nsha: {constants.GIT_SHA}"
        )
        await ctx.message.delete()
