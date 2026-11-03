"""Streamlit 메인 앱. 홈, 독립성 검토, 채팅, 그래프."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from frontend.api_client import get_health, API_BASE
from frontend.pages import chat, graph, independence


st.set_page_config(
    page_title="Audit Chat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Audit Chat")
st.caption("Streamlit + FastAPI + Neo4j + Mermaid + LLM")

# 사이드바: 메뉴·헬스
with st.sidebar:
    page = st.radio(
        "메뉴",
        ["홈", "독립성 검토", "채팅 (LLM)", "그래프 (Mermaid)"],
        label_visibility="collapsed",
    )
    st.divider()
    try:
        health = get_health()
        neo = "✅" if health.get("neo4j_connected") else "❌"
        st.caption(f"API: ok | Neo4j: {neo}")
    except Exception:
        st.caption("API 연결 실패 (서버 실행 여부 확인)")

if page == "홈":
    st.header("홈")
    st.markdown("""
    - **독립성 검토**: 감사 시나리오 → 관계 추출 + 독립성 분석 (GPT-4o-mini / GPT-4o).
    - **채팅 (LLM)**: API 서버 LLM과 대화합니다.
    - **그래프 (Mermaid)**: Neo4j 그래프를 Mermaid로 확인합니다.
    """)
    st.info("먼저 터미널에서 `./run.sh` 또는 API 서버(uvicorn)를 실행하세요.")
    st.markdown("---")
    st.markdown("**감사 독립성 UI**(일반 제출용)는 **API 서버** `/` 에서 제공됩니다.")
    st.markdown(f"[감사 독립성 UI 열기]({API_BASE}/)")
elif page == "독립성 검토":
    independence.render()
elif page == "채팅 (LLM)":
    chat.render()
elif page == "그래프 (Mermaid)":
    graph.render()
