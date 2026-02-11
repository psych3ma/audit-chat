#!/usr/bin/env bash
# CTO 권장: 프로젝트 가상환경 일괄 설정
# 사용: ./scripts/setup_venv.sh [python3 경로]
# 예: ./scripts/setup_venv.sh
# 예: ./scripts/setup_venv.sh python3.11

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

MIN_PYTHON_VERSION=3.9
PYTHON="${1:-python3}"
VENV_DIR="${VENV_DIR:-venv}"

echo "[1/4] Python 확인 (필요: >= ${MIN_PYTHON_VERSION})..."
if ! command -v "$PYTHON" &>/dev/null; then
  echo "오류: '$PYTHON'을 찾을 수 없습니다. Python ${MIN_PYTHON_VERSION}+ 를 설치하거나 경로를 지정하세요."
  echo "  예: ./scripts/setup_venv.sh python3.11"
  exit 1
fi

CURRENT=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! "$PYTHON" -c "import sys; sys.exit(0 if (sys.version_info.major, sys.version_info.minor) >= (3, 9) else 1)" 2>/dev/null; then
  echo "오류: Python ${CURRENT} 사용 중. 이 프로젝트는 Python >= ${MIN_PYTHON_VERSION} 이 필요합니다."
  exit 1
fi
echo "  사용 중: $("$PYTHON" --version)"

echo "[2/4] 가상환경 생성: $VENV_DIR/"
"$PYTHON" -m venv "$VENV_DIR"

echo "[3/4] pip 업그레이드 및 의존성 설치..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r requirements.txt --quiet

echo "[4/4] 검증..."
"$VENV_DIR/bin/python" -c "
from backend.config import get_settings
from backend.models.schemas import ChatRequest
print('  backend import OK')
"

echo ""
echo "가상환경 설정이 완료되었습니다."
echo "  활성화: source $VENV_DIR/bin/activate   # macOS/Linux"
echo "  활성화: $VENV_DIR\\\\Scripts\\\\activate   # Windows"
echo "  실행:   ./run.sh (또는 make run)"
