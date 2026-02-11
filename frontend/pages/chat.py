"""채팅 페이지: LLM과 대화."""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from frontend.api_client import post_chat
from frontend.components.mermaid_chart import render_mermaid


def render():
    st.subheader("Audit Chat (LLM)")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("mermaid"):
                render_mermaid(msg["mermaid"], height=300)

    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
                data = post_chat(messages)
                reply = data.get("message", {}).get("content", "")
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"API 오류: {e}")
                st.session_state.chat_history.pop()
