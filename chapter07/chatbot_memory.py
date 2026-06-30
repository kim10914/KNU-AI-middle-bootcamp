"""스트림릿 챗봇 — 랭체인 메시지 히스토리(메모리)로 멀티턴 구현

실행: streamlit run chapter07/chatbot_memory.py

핵심
- message_history.py 의 RunnableWithMessageHistory 를 스트림릿에 얹은 버전.
- 스트림릿은 입력마다 스크립트 전체를 다시 실행하므로, 대화 기록은
  일반 변수가 아니라 st.session_state 에 저장해야 유지된다.
- 화면 출력용 메시지(messages)와, 모델용 대화 기록(store)을 둘 다 보관한다.
- 답변은 stream() 으로 받아 .empty() 컨테이너에 타이핑하듯 출력한다.
"""

import streamlit as st
from langchain_openai import ChatOpenAI  # 오픈AI 모델을 사용하는 랭체인 챗봇 클래스
from langchain_core.chat_history import InMemoryChatMessageHistory  # 메모리에 대화 기록을 저장
from langchain_core.runnables.history import RunnableWithMessageHistory  # 메시지 기록을 끼워주는 래퍼
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

st.title("💬 Chatbot")

# 화면 표시용 메시지 기록 (최초 1회 시스템 메시지로 초기화)
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 사용자의 질문에 친절히 답하는 AI 챗봇이다.")
    ]

# 세션별 대화 기록을 저장할 딕셔너리 대신 session_state 사용
if "store" not in st.session_state:
    st.session_state["store"] = {}


def get_session_history(session_id: str):
    """세션 ID 별 대화 기록을 반환 (없으면 새로 생성)."""
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = InMemoryChatMessageHistory()
    return st.session_state["store"][session_id]


llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",  # 필수!
    api_key=os.getenv("OPENAI_API_KEY"),       # OpenRouter 전용 키
)

# 모델 + 메시지 히스토리 래퍼
with_message_history = RunnableWithMessageHistory(llm, get_session_history)
config = {"configurable": {"session_id": "abc2"}}

# 스트림릿 화면에 지난 메시지 출력
for msg in st.session_state.messages:
    if msg:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)

# 사용자 입력 처리
if prompt := st.chat_input():
    print("user:", prompt)
    st.session_state.messages.append(HumanMessage(prompt))  # 화면 기록에 추가
    st.chat_message("user").write(prompt)

    # 메시지 히스토리 래퍼로 스트림 응답 받기 (대화 맥락은 래퍼가 자동 관리)
    response = with_message_history.stream([HumanMessage(prompt)], config=config)

    # 스트림 조각을 누적하며 타이핑하듯 출력
    ai_response_bucket = None
    with st.chat_message("assistant").empty():
        for r in response:
            if ai_response_bucket is None:
                ai_response_bucket = r
            else:
                ai_response_bucket += r
            st.markdown(ai_response_bucket.content)  # 지금까지 모인 내용을 다시 그림

    msg = ai_response_bucket.content
    st.session_state.messages.append(ai_response_bucket)  # 화면 기록에 AI 응답 추가
    print("assistant:", msg)
