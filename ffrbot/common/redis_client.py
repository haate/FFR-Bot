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


@unique
class AdminKeys(Enum):
    ROLE_IDS = "admin_role_ids"
    POLLS_CATEGORY = "polls_category_id"
    ROLE_REQUESTS_CHANNEL = "role_requests_channel"


@unique
class RaceKeys(Enum):
    ORG_CHANNEL_ID = "org_channel_id"
    RESULTS_CHANNEL_ID = "results_channel_id"


Keys = Union[AdminKeys, RaceKeys]


def check_namespace_and_key(namespace: Namespace, key: Keys):
    if namespace is Namespace.ADMIN_CONFIG:
        assert key in AdminKeys
    elif namespace is Namespace.RACE_CONFIG:
        assert key in RaceKeys
    else:
        raise Exception


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

    def set_str(self, namespace: Namespace, key: Keys, value: str) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.set(str(namespace) + str(key), value)

    def get_str(self, namespace: Namespace, key: Keys) -> Optional[str]:
        check_namespace_and_key(namespace, key)
        return self.__db.get(str(namespace) + str(key))

    def set_obj(self, namespace: Namespace, key: Keys, value: object) -> None:
        check_namespace_and_key(namespace, key)
        self.__db.set(
            str(namespace) + str(key),
            pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
        )

    def get_obj(self, namespace: Namespace, key: Keys) -> Optional[object]:
        check_namespace_and_key(namespace, key)
        return pickle.loads(self.__db.get(str(namespace) + str(key)))

    def set_str_dict(
        self, namespace: Namespace, key: Keys, value: Dict[str, str]
    ) -> None:
        check_namespace_and_key(namespace, key)
        for k, v in value.items():
            self.__db.hset(str(namespace) + str(key), k, v)

    def get_str_dict(
        self, namespace: Namespace, key: Keys
    ) -> Optional[Dict[str, str]]:
        check_namespace_and_key(namespace, key)
        k_v_pairs = self.__db.hgetall(str(namespace) + str(key))
        if k_v_pairs is not None:
            return_value = dict()
            for k, v in k_v_pairs.items():
                return_value[k.decode("utf-8")] = v.decode("utf-8")
            return return_value

    def set_obj_dict(
        self, namespace: Namespace, key: Keys, value: Dict[str, Any]
    ) -> None:
        check_namespace_and_key(namespace, key)
        for k, v in value.items():
            self.__db.hset(
                str(namespace) + str(key),
                k,
                pickle.dumps(v, protocol=pickle.HIGHEST_PROTOCOL),
            )

    def get_obj_dict(
        self, namespace: Namespace, key: Keys
    ) -> Optional[Dict[str, Any]]:
        check_namespace_and_key(namespace, key)
        k_v_pairs = self.__db.hgetall(str(namespace) + str(key))
        if k_v_pairs is not None:
            return_value = dict()
            for k, v in k_v_pairs.items():
                return_value[k.decode("utf-8")] = pickle.loads(v)
            return return_value

    def set_set(
        self, namespace: Namespace, key: Keys, new: Iterable[str]
    ) -> None:
        check_namespace_and_key(namespace, key)
        current = self.__db.smembers(str(namespace) + str(key))

        to_remove = [x for x in current if x not in new]
        to_add = [x for x in new if x not in current]
        [self.__db.srem(str(namespace) + str(key), x) for x in to_remove]
        [self.__db.sadd(str(namespace) + str(key), x) for x in to_add]

    def get_set(self, namespace: Namespace, key: Keys) -> Optional[Set[str]]:
        check_namespace_and_key(namespace, key)
        return self.__db.smembers(str(namespace) + str(key))

    @property
    def raw(self) -> redis.Redis:
        return self.__db
