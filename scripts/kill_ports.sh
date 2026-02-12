#!/usr/bin/env bash
# 포트 8000, 8501 사용 중인 프로세스 종료 (Address already in use 해결)
# 사용: ./scripts/kill_ports.sh

set -e
cd "$(dirname "$0")/.."
API_PORT="${API_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

for port in $API_PORT $STREAMLIT_PORT; do
  pid=$(lsof -ti :"$port" 2>/dev/null || true)
  if [ -n "$pid" ]; then
    kill -9 $pid 2>/dev/null || true
    echo "Killed process $pid on port $port"
  else
    echo "Port $port: no process found"
  fi
done
echo "Done. Run ./run.sh again."
