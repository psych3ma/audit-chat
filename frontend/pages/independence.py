"""독립성 검토 페이지: 감사 시나리오 → 관계 추출 + 독립성 분석."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.api_client import post_independence_review
from frontend.components.mermaid_chart import render_mermaid

# 시나리오 6선 (감사 독립성 — PwC 정적 UI audit-chat-pwc.html 칩과 동일)
SCENARIOS = [
    "B회계법인 소속 이유명 공인회계사는 회계법인 퇴직 후 10개월 뒤에 B회계법인의 감사대상회사인 서울㈜의 재무담당임원으로 취임하였다. 이유명 공인회계사는 B회계법인 재직 당시 서울㈜의 재무제표 감사업무에 관여하지 않았다.",
    "공인회계사 자격증 소지자인 이대한씨는 경기㈜에서 경리과장으로 근무하던 중 20x8년 11월에 B회계법인 소속 공인회계사로 입사하였다. 20x9년 1월에 B회계법인과 경기㈜는 재무제표 감사계약을 체결하였다.",
    "B회계법인의 사원인 이영희 공인회계사는 직계비속의 사망으로 인하여 B회계법인의 감사대상회사 주식 0.5%를 소유하게 되었다.",
    "이지수 공인회계사는 B회계법인의 사원으로 근무하고 있으며, B회계법인은 경북㈜를 감사하고 있다. 이지수 공인회계사의 부친은 경북㈜의 대표이사로 재직 중이다.",
    "부산㈜의 재무제표감사 인증업무팀의 구성원인 이장래 공인회계사는 이번 부산㈜의 감사업무가 종료된 후에 부산㈜의 재무담당이사로 합류할 예정이다.",
    "이관상 공인회계사는 전남㈜의 대표이사의 부탁으로 회계부서 직원 채용면접심사에 참여하고 가장 적합한 후보자를 선발하여 추천하였다. 또한, 대표이사와 함께 최종면접에 참석하여 박수리씨를 회계팀장으로 선발하였다. 해당 연도에 이관상 공인회계사는 전남㈜의 재무제표에 대한 외부감사업무를 의뢰받았다.",
]
SCENARIO_LABELS = [
    "퇴직 후 감사대상회사 임원 취임",
    "전 경리과장 입사 후 감사계약",
    "직계비속 사망으로 주식 보유",
    "부친이 감사대상회사 대표이사",
    "감사 종료 후 재무담당이사 합류",
    "채용 참여 후 해당 연도 외부감사",
]

# Colab과 동일한 상태별 색상
STATUS_COLORS = {
    "수임 불가": "#d32f2f",
    "안전장치 적용 시 수임 가능": "#ed6c02",
    "수임 가능": "#2e7d32",
}


def render():
    st.subheader("독립성 검토 시스템")
    st.caption("감사 시나리오를 입력하면 관계 추출(GPT-4o-mini) 후 독립성 분석(GPT-4o)을 수행합니다.")

    st.markdown("**예시 시나리오 (6선)**")
    cols = st.columns(2)
    for i, (label, text) in enumerate(zip(SCENARIO_LABELS, SCENARIOS)):
        with cols[i % 2]:
            if st.button(label, key=f"scenario_{i}", use_container_width=True):
                st.session_state.independence_scenario = text
                st.rerun()

    scenario = st.text_area(
        "감사 시나리오",
        placeholder="위 버튼을 누르거나 직접 입력하세요.",
        height=150,
        label_visibility="collapsed",
        value=st.session_state.get("independence_scenario", ""),
        key="independence_scenario",
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
