"""스트림릿 챗봇 — 랭체인 메모리 없이 멀티턴 만들기

실행: streamlit run chapter07/chatbot_no_memory.py

핵심
- RunnableWithMessageHistory 같은 메모리 래퍼를 쓰지 않는다.
- 대신 st.session_state["messages"] 리스트에 모든 메시지를 직접 쌓고,
  매 턴 그 전체를 모델에 넘겨 맥락을 유지한다(가장 직관적인 방식).
- get_ai_response 는 stream() 결과를 그대로 yield 하는 제너레이터다.
  → st.write_stream() 에 넘기면 타이핑하듯 출력되고, 합쳐진 문자열을 돌려준다.
"""

import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",  # 필수!
    api_key=os.getenv("OPENAI_API_KEY"),       # OpenRouter 전용 키
)


# 사용자의 메시지를 처리하기 위한 함수
def get_ai_response(messages):
    """모델의 스트림 응답을 조각 단위로 흘려보내는 제너레이터."""
    response = llm.stream(messages)
    for chunk in response:
        yield chunk  # AIMessageChunk 하나씩 넘김


# Streamlit 앱
st.title("💬 GPT-4o Langchain Chat")

# 스트림릿 session_state 에 메시지 저장 (최초 1회 초기화)
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 사용자를 돕기 위해 최선을 다하는 인공지능 봇이다."),
        AIMessage("How can I help you?"),
    ]

# 스트림릿 화면에 지난 메시지 출력
for msg in st.session_state.messages:
    if msg.content:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)

# 사용자 입력 처리
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)                       # 사용자 메시지 출력
    st.session_state.messages.append(HumanMessage(prompt))     # 사용자 메시지 저장

    # 전체 대화 기록을 넘겨 응답 생성 (스트림)
    response = get_ai_response(st.session_state["messages"])

    result = st.chat_message("assistant").write_stream(response)  # AI 메시지 출력 (합쳐진 문자열 반환)
    st.session_state["messages"].append(AIMessage(result))       # AI 메시지 저장
