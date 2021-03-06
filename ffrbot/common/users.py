from .discord_user import DiscordUser
from discord.ext import commands
from .redis_client import RedisClient, Namespace, UserKeys
from typing import *


class Users(commands.Cog):
    def __init__(self, db: RedisClient):
        self.db = db
        self.users: Dict[str, DiscordUser] = dict()

    def load(self):
        user_ids: Set[str] = self.db.get_set(
            Namespace.USER_CONFIG, UserKeys.DISCORD_IDS
        )
        for user_id in user_ids:
            self.users[user_id] = DiscordUser(user_id, self.db)
