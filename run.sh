#!/usr/bin/env bash
# Audit Chat: Backend(FastAPI) + Frontend(Streamlit) 동시 실행
# Address already in use 시: ./scripts/kill_ports.sh 후 다시 실행

set -e
cd "$(dirname "$0")"

# 가상환경 자동 사용 (venv가 있으면 우선)
if [ -d "venv" ] && [ -x "venv/bin/python" ]; then
  export PATH="$(pwd)/venv/bin:$PATH"
  echo "Using venv: $(pwd)/venv"
fi

# .env 로드
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

API_PORT="${API_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

# 포트 선점 해제 (Errno 48 방지)
if [ -x "scripts/kill_ports.sh" ]; then
  ./scripts/kill_ports.sh
  sleep 2
fi

echo "Starting Backend (FastAPI) on port $API_PORT..."
uvicorn backend.main:app --host "${API_HOST:-0.0.0.0}" --port "$API_PORT" --reload &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$API_PORT/ready" 2>/dev/null | grep -q 200; then
    echo "Backend ready."
    break
  fi
  sleep 1
done

echo "Starting Frontend (Streamlit) on port $STREAMLIT_PORT..."
export API_BASE_URL="http://localhost:$API_PORT"
streamlit run frontend/app.py --server.port "$STREAMLIT_PORT" --server.address "${STREAMLIT_HOST:-0.0.0.0}" &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID | Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:$API_PORT | Docs: http://localhost:$API_PORT/docs"
echo "Frontend: http://localhost:$STREAMLIT_PORT"
echo "Press Ctrl+C to stop both."

# macOS Bash 3.x 호환: wait -n 대신 둘 중 하나 종료 시 나머지 정리
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT TERM
wait $BACKEND_PID $FRONTEND_PID
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
