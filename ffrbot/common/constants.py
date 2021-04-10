import os

SLEEP_TIME = 5000
try:
    BOT_ADMIN_ID = int(os.environ["BOT_ADMIN_ID"])
except KeyError:
    BOT_ADMIN_ID = 140605120579764226
try:
    VERSION = os.environ["BOT_VERSION"]
except KeyError:
    VERSION = "local development version"
try:
    GIT_SHA = os.environ["BOT_GIT_SHA"]
except KeyError:
    GIT_SHA = "local development sha"
