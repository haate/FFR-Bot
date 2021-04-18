#!/bin/bash
if [ "$1" ]; then
    DB=$1
else
    DB="db1"
fi

if [[  ! -e .data/$DB ]]; then
    mkdir -p .data/$DB
    mongod --port 27017 --dbpath .data/$DB &
    sleep 1
    mongo < initdb.js
    sleep 1
fi

mongod --auth --port 27017 --dbpath .data/$DB &
poetry run python3 -m ffrbot.dev
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT