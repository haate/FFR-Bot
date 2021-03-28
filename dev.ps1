Try {
#    $mongoJob = Start-Job -ScriptBlock { mongod --auth --port 27017 --dbpath ./.data/db1  }
    poetry run python3 -m ffrbot.dev
} Finally {
 #   Write-Host "Stopping mongodb job"
#    Remove-Job $mongoJob -Force
}


