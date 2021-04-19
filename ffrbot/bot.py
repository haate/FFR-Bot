import asyncio
import platform
import logging
import time

import discord
from discord.ext import commands
from pymongo import MongoClient
import os


from .cogs.racing.races import Races
from .cogs.roles import Roles
from .cogs.core import Core

# from .cogs.voting.polls import Polls
from .cogs.rng import RNG
from .cogs.users import Users
from .cogs.config import ConfigCommands
from .common import constants, config


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    db = MongoClient(
        os.environ.get("MONGO_HOST", "localhost"),
        int(os.environ.get("MONGO_PORT", 27017)),
        username=os.environ.get("MONGO_USER", "admin"),
        password=os.environ.get("MONGO_PASS", "password"),
    )

    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True

    description = "FFR discord bot"

    bot = commands.Bot(
        command_prefix="?",
        description=description,
        case_insensitive=True,
        intents=intents,
    )

    config.init(db, bot)
    logging.info("initializing bot.")

    bot.add_cog(Core(bot, db))
    bot.add_cog(Races(bot, db))
    bot.add_cog(Roles(bot, db))
    # bot.add_cog(Polls(bot, db))
    bot.add_cog(RNG(bot))
    bot.add_cog(Users(bot, db))
    bot.add_cog(ConfigCommands(bot))

    @bot.event
    async def on_ready() -> None:
        logging.info(f"python version: {platform.python_version()}")
        logging.info(f"discord.py version: {discord.__version__}")
        logging.info("Logged in as")
        logging.info(bot.user.name)
        logging.info(bot.user.id)
        logging.info("------")

    @bot.event
    async def on_command_completion(ctx: commands.Context) -> None:
        msg: discord.Message = ctx.message

        try:
            await msg.add_reaction("✔")
        except Exception as e:
            logging.debug(
                f"on_command_completion exception: {repr(e)},"
                f" original command possibly deleted"
            )

    @bot.event
    async def on_command_error(
        ctx: commands.Context, error: commands.CommandError
    ) -> None:
        msg: discord.Message = ctx.message
        logging.warning("command error: " + str(error))
        try:
            await msg.add_reaction("✖")
        except Exception as e:
            logging.debug(
                f"on_command_error exception: {repr(e)},"
                f" original command possibly deleted"
            )

    def handle_exit(
        client: commands.Bot, loop: asyncio.AbstractEventLoop
    ) -> None:
        # taken from https://stackoverflow.com/a/50981577
        loop.run_until_complete(client.logout())
        for t in asyncio.Task.all_tasks(loop=loop):
            if t.done():
                t.exception()
                continue
            t.cancel()
            try:
                loop.run_until_complete(asyncio.wait_for(t, 5, loop=loop))
                t.exception()
            except asyncio.InvalidStateError:
                pass
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                pass

    def run_client(client: commands.Bot, token: str) -> None:
        loop = asyncio.get_event_loop()
        while True:
            try:
                logging.info("Starting connection")
                loop.run_until_complete(client.start(token))
            except KeyboardInterrupt:
                handle_exit(client, loop)
                client.loop.close()
                logging.info("Program ended")
                break
            except Exception as e:
                logging.exception(e)
                handle_exit(client, loop)
            logging.info("Waiting until restart")
            time.sleep(constants.SLEEP_TIME)

    with open("ffrbot/token.txt", "r") as f:
        token = f.read()
    token = token.strip()

    run_client(bot, token)
