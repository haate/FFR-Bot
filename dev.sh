if uname -a | grep microsoft; then
  echo "WSL detected using 'uname -a' (output above), please use dev.ps1 as there are filesystem event issues in WSL"
  exit
fi
redis-server &
python3 -m ffrbot.dev
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT