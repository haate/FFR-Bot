$redisJob = Start-Job -ScriptBlock { redis-server }
poetry run python3 -m ffrbot.dev

Remove-Job $redisJob
