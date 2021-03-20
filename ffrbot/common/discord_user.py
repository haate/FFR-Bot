from .redis_client import RedisClient, Namespace, UserKeys
from typing import *
from .config import get_guild
import discord


class DiscordUser:
    def __init__(self, user_id: int, db: RedisClient):
        self.user_id = user_id
        self.__db: RedisClient = db
        self.__twitch_id: Optional[str] = None

    @property
    def display_name(self) -> str:
        member: Optional[discord.Member] = get_guild().get_member(self.user_id)
        return member.display_name if member else ""

    @property
    def name(self) -> str:
        member: Optional[discord.Member] = get_guild().get_member(self.user_id)
        return member.name if member else ""

    @property
    def twitch_id(self) -> Optional[str]:
        return self.__db.get_str_dict_item(
            Namespace.USER_CONFIG, UserKeys.TWITCH_IDS, str(self.user_id)
        )

    @twitch_id.setter
    def twitch_id(self, value: str) -> None:
        self.__db.set_str_dict_item(
            Namespace.USER_CONFIG,
            UserKeys.TWITCH_IDS,
            str(self.user_id),
            value,
        )

    @twitch_id.deleter
    def twitch_id(self) -> None:
        self.__db.del_str_dict_item(
            Namespace.USER_CONFIG,
            UserKeys.TWITCH_IDS,
            str(self.user_id),
        )

    def delete(self) -> None:
        """
        This deletes all bot saved data about this user
        """
        del self.twitch_id
