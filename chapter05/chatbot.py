"""Streamlit 웹 챗봇 (함수 호출 / tool use 예제)

실행: streamlit run chapter05/chatbot.py
- get_current_time 도구를 통해 "지금 몇 시야?" 같은 질문에 답한다.
- 대화 기록은 st.session_state 에 보관해 재실행에도 유지된다.
"""

from get_function import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

SYSTEM_PROMPT = (
    "너는 사용자를 도와주는 비서야. "
    "사용자가 현재 시간을 물어볼 때 어느 지역(타임존) 기준인지 명확하지 않으면, "
    "도구를 호출하지 말고 먼저 어느 지역 기준인지 사용자에게 되물어봐."
)


def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages,
        tools=tools,
    )
    return response


st.title("💬 Chatbot")

# 대화 기록 초기화 (최초 1회만). Streamlit 은 입력마다 스크립트를 다시 실행하므로
# 일반 변수가 아닌 session_state 에 저장해야 대화가 이어진다.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 이전 대화 다시 그리기 (system / tool 메시지는 화면에 표시하지 않음)
for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 처리
if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 1차 호출: 모델이 필요하면 도구 호출을 요청한다.
    ai_message = get_ai_response(st.session_state.messages, tools=tools).choices[0].message
    tool_calls = ai_message.tool_calls

    if tool_calls:
        # tool 결과보다 먼저 tool_calls 가 담긴 assistant 메시지를 추가해야 한다.
        # 다시 그리기 루프에서 dict 처럼 다루므로 model_dump() 로 dict 변환해 저장.
        st.session_state.messages.append(ai_message.model_dump())

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)

            if tool_name == "get_current_time":
                result = get_current_time(timezone=arguments.get("timezone"))
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

        # 2차 호출: 도구 실행 결과를 바탕으로 최종 답변을 생성한다.
        ai_message = get_ai_response(st.session_state.messages, tools=tools).choices[0].message

    content = ai_message.content or "(응답 없음)"
    st.session_state.messages.append({"role": "assistant", "content": content})
    st.chat_message("assistant").write(content)
