$redisJob = Start-Job -ScriptBlock { redis-server }
python3 -m ffrbot.dev

Remove-Job $redisJob
