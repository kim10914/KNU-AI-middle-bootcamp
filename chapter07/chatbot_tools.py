"""스트림릿 챗봇 — 도구(tool) 추가하고 스트림 방식으로 출력하기

실행: streamlit run chapter07/chatbot_tools.py

핵심
- chatbot_no_memory.py 에 '도구 호출' 기능을 더한 완성형 에이전트 챗봇.
- 핵심 변경점
    ① llm.stream() → llm_with_tools.stream() 으로 변경 (도구 사용 가능)
    ② 스트림으로 오는 tool_call 청크를 gathered 변수에 하나로 합친다.
    ③ gathered.tool_calls 가 있으면 도구를 실행하고, 그 결과(ToolMessage)를
      메시지에 추가한 뒤 get_ai_response 를 '재귀 호출'해 최종 답변까지 만든다.
- 도구 호출 메시지(ToolMessage)도 화면에 표시한다.
"""

import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from datetime import datetime
import pytz

load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",  # 필수!
    api_key=os.getenv("OPENAI_API_KEY"),       # OpenRouter 전용 키
)


# ───────────────────────────────────────────────
# 도구 함수 정의
# ───────────────────────────────────────────────
@tool
def get_current_time(timezone: str, location: str) -> str:
    """현재 시각을 반환하는 함수.

    Args:
        timezone (str): 타임존 (예: 'Asia/Seoul') 실제 존재하는 타임존이어야 함
        location (str): 지역명. 이후 llm 답변 생성에 사용됨
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        result = f'{timezone} ({location}) 현재시각 {now}'
        print(result)
        return result
    except pytz.UnknownTimeZoneError:
        return f"알 수 없는 타임존: {timezone}"


# 도구 바인딩
tools = [get_current_time]
tool_dict = {"get_current_time": get_current_time}

llm_with_tools = llm.bind_tools(tools)


# 사용자의 메시지 처리하기 위한 함수
def get_ai_response(messages):
    """스트림 응답을 흘려보내며, 도구 호출이 필요하면 처리 후 재귀로 최종 답변까지 만든다."""
    response = llm_with_tools.stream(messages)  # ① llm.stream() 을 llm_with_tools.stream() 으로 변경

    gathered = None  # ② 조각난 tool_call 을 합칠 변수
    for chunk in response:
        yield chunk  # 화면 출력을 위해 조각을 먼저 흘려보낸다.

        # ③ 청크 누적 (AIMessageChunk 는 += 로 합칠 수 있다)
        if gathered is None:
            gathered = chunk
        else:
            gathered += chunk

    # 도구 호출이 있으면 실제로 실행한다.
    if gathered.tool_calls:
        st.session_state.messages.append(gathered)  # 도구 호출을 요청한 AIMessage 기록

        for tool_call in gathered.tool_calls:
            selected_tool = tool_dict[tool_call["name"]]  # 도구 이름으로 도구 함수 선택
            tool_msg = selected_tool.invoke(tool_call)    # 도구 함수를 호출해 결과를 반환
            print(tool_msg, type(tool_msg))
            st.session_state.messages.append(tool_msg)    # 도구 결과(ToolMessage)를 기록

        # 도구 결과를 반영해 최종 답변을 다시 스트림으로 생성 (재귀 호출)
        for chunk in get_ai_response(st.session_state.messages):
            yield chunk


# Streamlit 앱
st.title("💬 GPT-4o Langchain Chat")

# 스트림릿 session_state 에 메시지 저장
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
        elif isinstance(msg, ToolMessage):  # 도구 호출 결과도 화면에 표시
            st.chat_message("tool").write(msg.content)

# 사용자 입력 처리
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)                    # 사용자 메시지 출력
    st.session_state.messages.append(HumanMessage(prompt))  # 사용자 메시지 저장

    response = get_ai_response(st.session_state["messages"])

    result = st.chat_message("assistant").write_stream(response)  # AI 메시지 출력
    st.session_state["messages"].append(AIMessage(result))       # AI 메시지 저장
