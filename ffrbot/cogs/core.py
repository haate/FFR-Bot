from typing import *

from ffrbot.common import constants, checks, config, snippits
from ffrbot.common.redis_client import RedisClient

from discord.ext import commands
from discord.utils import get
import discord

import logging


def allow_seed_rolling(ctx):
    return (ctx.channel.name == constants.call_for_races_channel) or (
        ctx.channel.category_id == get(ctx.guild.categories, name="races").id
    )


class Core(commands.Cog):
    """
    Core bot commands
    """

    def __init__(self, bot: commands.Bot, db: RedisClient):
        self.bot: commands.Bot = bot
        self.db: RedisClient = db

    @commands.command()
    @checks.is_bot_admin()
    async def init_guild(self, ctx: commands.Context) -> None:
        """
        Sets the guild (internal name for discord servers) that the bot will be
        used in.
        """
        logging.info("initializing bot in guild.")
        guild: discord.Guild = ctx.guild

        async def yes():

            config.set_guild_id(guild.id)
            logging.info("Guild set to: " + guild.name)

        async def no():
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
    async def purge(self, ctx):
        """
        Clears the channel history -- for testing
        """

        async def yes():
            await ctx.channel.purge(limit=100000)

        await snippits.wait_for_yes_no(
            self.bot,
            ctx,
            "Are you sure you want to delete this channel's message"
            " history entirely? This is not revertible",
            yes,
        )

    @commands.command(aliases=["whoami"])
    async def who_am_i(self, ctx):
        """
        Messages you your discord user id
        """
        await ctx.author.send(ctx.author.id)
        await ctx.message.delete()
