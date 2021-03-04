class DiscordUser:
    def __init__(self, user_id: str, name: str, display_name: str):
        self.user_id = user_id
        self.name = name
        self.display_name = display_name
        self.__twitch_id = None

    @property
    def twitch_id(self) -> str:
        return self.__twitch_id

    @twitch_id.setter
    def twitch_id(self, value: str) -> None:
        self.__twitch_id = value

    @twitch_id.deleter
    def twitch_id(self) -> None:
        del self.__twitch_id
