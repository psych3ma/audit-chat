"""그래프 페이지: Neo4j → Mermaid 시각화."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.api_client import get_graph_mermaid
from frontend.components.mermaid_chart import render_mermaid


def render():
    st.subheader("Graph (Neo4j → Mermaid)")
    if st.button("그래프 새로고침"):
        st.rerun()
    try:
        data = get_graph_mermaid()
        code = data.get("mermaid_code", "")
        desc = data.get("description", "")
        if desc:
            st.caption(desc)
        render_mermaid(code, height=500)
    except Exception as e:
        st.error(f"그래프를 불러올 수 없습니다. 백엔드/Neo4j를 확인하세요. {e}")
