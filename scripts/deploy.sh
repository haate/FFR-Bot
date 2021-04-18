#!/bin/bash
Mode=$1

if [ "$Mode" = "lint-fix" ]; then
    python -m autopep8 --aggressive --aggressive --experimental --max-line-length 79 -i -r ./src
fi

#
#if [ "$Mode" != "no-lint" ]; then
#  $LinterPassed=$(python3 -m flake8 --show-source --statistics ./src)
#    if [ "$LinterPassed" ]; then
#        echo $LinterPassed
#    fi
#fi

docker container stop ffrbot -t 0
docker container rm ffrbot
docker container stop ffrbot-db -t 0
docker container rm ffrbot-db
docker build -t ffrbot:local-test -f ./Dockerfile .
docker run -d --network=redis-network --name ffrbot-db --mount source=ffrbotvol,target=/data -d redis --appendonly yes
docker run --name ffrbot --network=redis-network -e REDIS_HOST=ffrbot-db -it ffrbot:local-test
