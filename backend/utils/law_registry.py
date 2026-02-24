"""법령명 → 국가법령정보센터(law.go.kr) URL 조회.

- 단일 소스: 법령검색목록.csv(법령MST·법령명) 기반.
- 조문 링크(제N조): 한글 경로 https://www.law.go.kr/법령/{법령명}/{조문} (해당 조문으로 바로 이동).
- 전체 법령 링크: lsInfoP.do?lsiSeq={법령MST}.
- 확장: CSV 경로는 설정(LAW_CSV_PATH) 또는 기본 위치(프로젝트 루트 법령검색목록.csv).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional
# 조문 직접 링크
LAW_GO_KR_ARTICLE_BASE = "https://www.law.go.kr"
# 전체 법령 본문
LAW_GO_KR_LSINFO_BASE = "https://www.law.go.kr/LSW/lsInfoP.do"

# 약칭 → 법령명
ALIASES: dict[str, str] = {
    "외부감사법": "주식회사 등의 외부감사에 관한 법률",
    "외부감사법 시행령": "주식회사 등의 외부감사에 관한 법률 시행령",
    "외부감사법 시행규칙": "주식회사 등의 외부감사에 관한 법률 시행규칙",
}

_registry: Optional[dict[str, str]] = None


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_csv_path() -> Path:
    return _project_root() / "법령검색목록.csv"


def _parse_csv(path: Path) -> list[tuple[str, str]]:
    """CSV에서 (법령명, 법령MST) 쌍 목록 반환. 첫 줄 '총N건'은 스킵."""
    rows: list[tuple[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        first = next(reader, None)
        if not first:
            return rows
        if "법령MST" in first:
            header = first
        elif len(first) == 1 and "총" in (first[0] or ""):
            header = next(reader, None)
        else:
            header = first
        if not header or "법령MST" not in header:
            return rows
        try:
            idx_mst = header.index("법령MST")
            idx_name = header.index("법령명")
        except ValueError:
            return rows
        for row in reader:
            if len(row) <= max(idx_mst, idx_name):
                continue
            mst = (row[idx_mst] or "").strip()
            name = (row[idx_name] or "").strip()
            if mst and name:
                rows.append((name, mst))
    return rows


def _build_registry(csv_path: Optional[Path] = None) -> dict[str, str]:
    """법령명(그대로) -> lsiSeq. 동일 법령명이면 나중 행이 덮어씀."""
    path = csv_path or _default_csv_path()
    if not path.is_file():
        return {}
    pairs = _parse_csv(path)
    return {name: mst for name, mst in pairs}


_ARTICLE_SUFFIX_PATTERN = r"제\d+조의?\d*"
_ARTICLE_FULL_PATTERN = re.compile(rf"^(.+?)\s+({_ARTICLE_SUFFIX_PATTERN})\s*$")
_ARTICLE_STRIP_PATTERN = re.compile(rf"\s*{_ARTICLE_SUFFIX_PATTERN}\s*$")


def _parse_article_ref(raw: str) -> Optional[tuple[str, str]]:
    """'공인회계사법 제21조' → (법령명, 조문). 매칭 실패 시 None."""
    s = (raw or "").strip()
    if not s:
        return None
    m = _ARTICLE_FULL_PATTERN.match(s)
    if not m:
        return None
    law_name = m.group(1).strip()
    article = m.group(2).strip()
    if law_name and article:
        return (law_name, article)
    return None


def strip_article_from_name(law_name: str) -> str:
    """법령명에서 조문 부분 제거. 예: '공인회계사법 제21조' → '공인회계사법'"""
    return _ARTICLE_STRIP_PATTERN.sub("", (law_name or "").strip()).strip()


def _build_article_url(law_name: str, article: str) -> str:
    """조문 직접 링크 생성 (한글 경로)."""
    return f"{LAW_GO_KR_ARTICLE_BASE}/법령/{law_name}/{article}"


def _normalize_candidates(raw: str) -> list[str]:
    """매칭 후보 법령명 목록 (전체 → 조문 제거 → 별칭)."""
    s = (raw or "").strip()
    if not s:
        return []
    candidates = [s]
    no_jo = strip_article_from_name(s)
    if no_jo and no_jo != s:
        candidates.append(no_jo)
    if s in ALIASES:
        candidates.append(ALIASES[s])
    return candidates


def get_registry(force_reload: bool = False) -> dict[str, str]:
    """법령명 → lsiSeq 매핑(캐시)."""
    global _registry
    if _registry is not None and not force_reload:
        return _registry
    try:
        from backend.config import get_settings
        p = get_settings().law_csv_path.strip()
        csv_path = Path(p) if p else _default_csv_path()
    except Exception:
        csv_path = _default_csv_path()
    _registry = _build_registry(csv_path)
    return _registry


def get_law_url(law_name: str) -> Optional[str]:
    """법령 표기 → law.go.kr URL (조문 링크 또는 전체 본문)."""
    s = (law_name or "").strip()
    if not s:
        return None
    reg = get_registry()
    parsed = _parse_article_ref(s)
    if parsed:
        base_name, article = parsed
        for candidate in _normalize_candidates(s):
            name_for_lookup = strip_article_from_name(candidate) or candidate
            if name_for_lookup in reg:
                return _build_article_url(name_for_lookup, article)
        return _build_article_url(base_name, article)
    for candidate in _normalize_candidates(s):
        if candidate in reg:
            return f"{LAW_GO_KR_LSINFO_BASE}?lsiSeq={reg[candidate]}"
    return None


def clear_cache() -> None:
    """캐시 초기화."""
    global _registry
    _registry = None


def is_valid_law(law_name: str) -> bool:
    """법령명이 CSV 레지스트리에 존재하는지 확인."""
    s = (law_name or "").strip()
    if not s:
        return False
    reg = get_registry()
    base_name = strip_article_from_name(s) or s
    if base_name in reg:
        return True
    if base_name in ALIASES and ALIASES[base_name] in reg:
        return True
    return False
