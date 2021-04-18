#!/bin/bash
if [ "$1" ]; then
    D=$1
else
    D="ffrbot"
fi

poetry run watch dmypy run $D

trap "poetry run dmypy stop" SIGINT SIGTERM EXIT
