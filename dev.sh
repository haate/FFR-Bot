redis-server &
poetry run python3 -m ffrbot.dev
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
