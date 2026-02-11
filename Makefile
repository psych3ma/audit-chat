# Audit Chat - CTO 권장 타깃
# 사용: make [target]

PYTHON   ?= python3
VENV     ?= venv
PIP      := $(VENV)/bin/pip
PY       := $(VENV)/bin/python

.PHONY: venv install run clean help

help:
	@echo "Audit Chat - 가상환경 및 실행"
	@echo "  make venv    - 가상환경 생성 + 의존성 설치 (scripts/setup_venv.sh 호출)"
	@echo "  make install - 기존 venv에 의존성만 설치"
	@echo "  make run     - 백엔드+프론트 동시 실행 (run.sh)"
	@echo "  make clean   - venv 및 캐시 삭제"

venv:
	@chmod +x scripts/setup_venv.sh 2>/dev/null || true
	@./scripts/setup_venv.sh $(PYTHON)

install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt

$(VENV)/bin/activate:
	@echo "venv가 없습니다. 'make venv' 를 먼저 실행하세요."
	@exit 1

run:
	./run.sh

clean:
	rm -rf $(VENV) .pytest_cache __pycache__ backend/__pycache__ frontend/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "정리 완료."
