"""Mermaid 다이어그램 렌더링 컴포넌트."""
import streamlit as st

try:
    from streamlit_mermaid import st_mermaid
except ImportError:
    st_mermaid = None


def render_mermaid(mermaid_code: str, height: int = 400) -> None:
    """Mermaid 코드를 스트림릿에 렌더링."""
    if not mermaid_code or not mermaid_code.strip():
        st.info("표시할 Mermaid 코드가 없습니다.")
        return
    if st_mermaid is None:
        st.code(mermaid_code, language="mermaid")
        st.caption("streamlit-mermaid 미설치 시 코드만 표시됩니다. pip install streamlit-mermaid")
        return
    st_mermaid(mermaid_code, height=height)
