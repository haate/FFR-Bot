from .redis_client import RedisClient, Namespace, UserKeys


class DiscordUser:
    def __init__(self, user_id: str, db: RedisClient):
        self.user_id = user_id
        self.__db: RedisClient = db

    @property
    def display_name(self) -> str:
        return self.__db.get_str_dict_item(
            Namespace.USER_CONFIG, UserKeys.DISPLAY_NAMES, self.user_id
        )

    @display_name.setter
    def display_name(self, value: str) -> None:
        self.__db.set_str_dict_item(
            Namespace.USER_CONFIG, UserKeys.DISPLAY_NAMES, self.user_id, value
        )

    @display_name.deleter
    def display_name(self) -> None:
        del self.__twitch_id

    @property
    def name(self) -> str:
        return self.__twitch_id

    @name.setter
    def name(self, value: str) -> None:
        self.__twitch_id = value

    @name.deleter
    def name(self) -> None:
        del self.__twitch_id

    @property
    def twitch_id(self) -> str:
        return self.__twitch_id

    @twitch_id.setter
    def twitch_id(self, value: str) -> None:
        self.__twitch_id = value

    @twitch_id.deleter
    def twitch_id(self) -> None:
        del self.__twitch_id
