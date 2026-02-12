"""독립성 검토 페이지: 감사 시나리오 → 관계 추출 + 독립성 분석."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.api_client import post_independence_review
from frontend.components.mermaid_chart import render_mermaid

# Colab과 동일한 상태별 색상
STATUS_COLORS = {
    "수임 불가": "#d32f2f",
    "안전장치 적용 시 수임 가능": "#ed6c02",
    "수임 가능": "#2e7d32",
}


def render():
    st.subheader("독립성 검토 시스템")
    st.caption("감사 시나리오를 입력하면 관계 추출(GPT-4o-mini) 후 독립성 분석(GPT-4o)을 수행합니다.")

    scenario = st.text_area(
        "감사 시나리오",
        placeholder="여기에 감사 시나리오를 입력하세요...",
        height=150,
        label_visibility="collapsed",
    )

    if st.button("분석 시작", type="primary", use_container_width=True):
        if not (scenario and scenario.strip()):
            st.warning("시나리오를 입력해 주세요.")
            return

        with st.spinner("분석 중... (관계 추출 → 독립성 분석)"):
            try:
                result = post_independence_review(scenario.strip())
            except Exception as e:
                st.error(f"API 오류: {e}")
                return

        trace_id = result.get("trace_id", "")
        analysis = result.get("analysis", {})
        mermaid_code = result.get("mermaid_code", "")

        status = analysis.get("status", "")
        risk_level = analysis.get("risk_level", "")
        color = STATUS_COLORS.get(status, "#455a64")

        st.markdown(
            f'<div style="background: {color}; color: white; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1rem;">'
            f'<strong>{status}</strong> (위험도: {risk_level}) &nbsp; <small>ID: {trace_id}</small>'
            f"</div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### 관계도")
            render_mermaid(mermaid_code, height=320)
            key_issues = analysis.get("key_issues") or []
            if key_issues:
                st.markdown("**주요 이슈**")
                for issue in key_issues:
                    st.markdown(f"- :red[{issue}]")
            else:
                st.caption("위반 사항 없음")

        with col2:
            st.markdown("#### 검토 의견")
            considerations = analysis.get("considerations", "")
            st.markdown(considerations or "-")
            st.markdown("---")
            safeguards = analysis.get("suggested_safeguards") or []
            st.markdown("**권고 안전장치**")
            if safeguards:
                for s in safeguards:
                    st.markdown(f"- {s}")
            else:
                st.caption("추가 조치 필요 없음")

        legal = analysis.get("legal_references")
        if legal:
            with st.expander("법규 참조"):
                for ref in legal:
                    st.markdown(f"- {ref}")
