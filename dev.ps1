Try {
    $redisJob = Start-Job -ScriptBlock { redis-server }
    poetry run python3 -m ffrbot.dev
} Finally {
    Write-Host "Stopping redis server job"
    Remove-Job $redisJob -Force
}


