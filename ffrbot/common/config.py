from .redis_client import *

__db: RedisClient


def init(db):
    global __db
    __db = db


def get_admin_role_ids() -> Set[str]:
    return __db.get_set(Namespace.ADMIN_CONFIG, AdminKeys.ROLE_IDS) or set()


def set_admin_role_ids(new_admins: Iterable[str]):
    current_admins = get_admin_role_ids()

    __db.set_set(
        Namespace.ADMIN_CONFIG,
        AdminKeys.ROLE_IDS,
        current_admins.union(set(new_admins)),
    )


def get_polls_category_id() -> str:
    return __db.get_str(Namespace.ADMIN_CONFIG, AdminKeys.POLLS_CATEGORY) or ""


def set_polls_category_id(value):
    __db.set_str(Namespace.ADMIN_CONFIG, AdminKeys.POLLS_CATEGORY, value)


def get_role_requests_channel_id() -> str:
    r_val = (
        __db.get_str(Namespace.ADMIN_CONFIG, AdminKeys.ROLE_REQUESTS_CHANNEL)
        or ""
    )
    logging.warning("find me " + r_val)
    return r_val


def set_role_requests_channel_id(value):
    __db.set_str(
        Namespace.ADMIN_CONFIG, AdminKeys.ROLE_REQUESTS_CHANNEL, value
    )


def get_race_org_channel_id() -> str:
    return __db.get_str(Namespace.RACE_CONFIG, RaceKeys.ORG_CHANNEL_ID) or ""


def set_race_org_channel_id(value):
    __db.set_str(Namespace.RACE_CONFIG, RaceKeys.ORG_CHANNEL_ID, value)


def get_race_results_channel_id() -> str:
    return (
        __db.get_str(Namespace.RACE_CONFIG, RaceKeys.RESULTS_CHANNEL_ID) or ""
    )


def set_race_results_channel_id(value):
    __db.set_str(Namespace.RACE_CONFIG, RaceKeys.RESULTS_CHANNEL_ID, value)
