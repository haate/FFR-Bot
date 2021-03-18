import redis
import logging
import os
import pickle
from typing import *
from enum import Enum, unique


@unique
class Namespace(Enum):
    ADMIN_CONFIG = "admin_config"
    RACE_CONFIG = "race_config"
    USER_CONFIG = "user_config"
    ROLE_CONFIG = "role_config"


@unique
class AdminKeys(Enum):
    ROLE_IDS = "admin_role_ids"
    POLLS_CATEGORY = "polls_category_id"
    ROLE_REQUESTS_CHANNEL = "role_requests_channel"
    GUILD_ID = "guild_id"


@unique
class RaceKeys(Enum):
    ORG_CHANNEL_ID = "org_channel_id"
    RESULTS_CHANNEL_ID = "results_channel_id"
    SYNC_RACES = "sync_races"
    ASYNC_RACES = "async_races"


@unique
class UserKeys(Enum):
    TWITCH_IDS = "twitchids"
    DISCORD_IDS = "discord_ids"
    DISPLAY_NAMES = "display_names"
    NAMES = "names"


@unique
class RoleKeys(Enum):
    SELF_ASSIGNABLE_ROLE_IDS = "self_assignable_role_ids"
    SELF_ASSIGNABLE_ROLE_DESCRIPTIONS = "self_assignable_role_descriptions"
    SELF_ASSIGNABLE_ROLE_NAMES = "self_assignable_role_names"


Keys = Union[AdminKeys, RaceKeys, UserKeys, RoleKeys]


def check_namespace_and_key(
    namespace: Namespace, key: Union[Keys, List[Keys]]
):
    def check(n, m):
        if n is Namespace.ADMIN_CONFIG:
            assert m in AdminKeys
        elif n is Namespace.RACE_CONFIG:
            assert m in RaceKeys
        elif n is Namespace.ROLE_CONFIG:
            assert m in RoleKeys
        elif n is Namespace.USER_CONFIG:
            assert m in UserKeys
        else:
            logging.error("Missing Namespace in check_namespace_and_key")
            raise Exception

    check(namespace, key)


def join(namespace, key) -> str:
    return str(namespace) + "_" + str(key)


class RedisClient:
    def __init__(self) -> None:
        redis_pool = redis.ConnectionPool(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=False,
        )
        db = redis.Redis(connection_pool=redis_pool)
        logging.info(db.info())
        self.__db = db

    def set_str(
        self, namespace: Namespace, key: Union[Keys, List[Keys]], value: str
    ) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.set(join(namespace, key), value)

    def get_str(self, namespace: Namespace, key: Keys) -> Optional[str]:
        check_namespace_and_key(namespace, key)
        string_bytes: Optional[bytes] = self.__db.get(join(namespace, key))
        return (
            string_bytes.decode("utf-8") if string_bytes is not None else None
        )

    def set_obj(self, namespace: Namespace, key: Keys, value: object) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.set(
            join(namespace, key),
            pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
        )

    def get_obj(self, namespace: Namespace, key: Keys) -> Optional[object]:
        check_namespace_and_key(namespace, key)
        obj: Optional[bytes] = self.__db.get(join(namespace, key))
        return pickle.loads(obj) if obj is not None else None

    def set_str_dict(
        self, namespace: Namespace, key: Keys, value: Dict[str, str]
    ) -> None:
        check_namespace_and_key(namespace, key)
        for k, v in value.items():
            self.__db.hset(join(namespace, key), k, v)

    def get_str_dict(
        self, namespace: Namespace, key: Keys
    ) -> Optional[Dict[str, str]]:
        check_namespace_and_key(namespace, key)
        k_v_pairs = self.__db.hgetall(join(namespace, key))
        if k_v_pairs is not None:
            return_value = dict()
            for k, v in k_v_pairs.items():
                return_value[k.decode("utf-8")] = v.decode("utf-8")
            return return_value

    def set_str_dict_item(
        self, namespace: Namespace, key: Keys, item_key: str, value: str
    ) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.hset(join(namespace, key), item_key, value)

    def get_str_dict_item(
        self, namespace: Namespace, key: Keys, item_key: str
    ) -> Optional[str]:
        logging.info(namespace)
        check_namespace_and_key(namespace, key)
        v: bytes = self.__db.hget(join(namespace, key), item_key)
        return v.decode("utf-8") if v else None

    def del_str_dict_item(
        self, namespace: Namespace, key: Keys, item_key: str
    ) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.hdel(join(namespace, key), item_key)

    def set_obj_dict(
        self, namespace: Namespace, key: Keys, value: Dict[str, Any]
    ) -> None:
        check_namespace_and_key(namespace, key)
        for k, v in value.items():
            self.__db.hset(
                join(namespace, key),
                k,
                pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL),
            )

    def get_obj_dict(
        self, namespace: Namespace, key: Keys
    ) -> Optional[Dict[str, Any]]:
        check_namespace_and_key(namespace, key)
        k_v_pairs = self.__db.hgetall(join(namespace, key))
        if k_v_pairs is not None:
            return_value = dict()
            for k, v in k_v_pairs.items():
                return_value[k.decode("utf-8")] = pickle.loads(v)
            return return_value

    def set_set(
        self, namespace: Namespace, key: Keys, new: Iterable[str]
    ) -> None:
        check_namespace_and_key(namespace, key)
        current = self.__db.smembers(join(namespace, key))
        to_remove = [x for x in current if x not in new]
        to_add = [x for x in new if x not in current]
        [self.__db.srem(join(namespace, key), x) for x in to_remove]
        [self.__db.sadd(join(namespace, key), x) for x in to_add]

    def get_set(self, namespace: Namespace, key: Keys) -> Optional[Set[str]]:
        check_namespace_and_key(namespace, key)
        return set(
            [
                x.decode("utf-8")
                for x in self.__db.smembers(join(namespace, key))
            ]
        )

    def set_int_set(
        self, namespace: Namespace, key: Keys, new: Iterable[int]
    ) -> None:
        check_namespace_and_key(namespace, key)
        current = self.__db.smembers(join(namespace, key))
        to_remove = [x for x in current if str(x) not in new]
        to_add = [x for x in new if x not in current]
        [self.__db.srem(join(namespace, key), x) for x in to_remove]
        [self.__db.sadd(join(namespace, key), x) for x in to_add]

    def get_int_set(
        self, namespace: Namespace, key: Keys
    ) -> Optional[Set[int]]:
        check_namespace_and_key(namespace, key)
        return set(
            [
                x.decode("utf-8")
                for x in self.__db.smembers(join(namespace, key))
            ]
        )

    @property
    def raw(self) -> redis.Redis:
        return self.__db
