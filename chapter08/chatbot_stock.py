from gpt_functions import (
    get_current_time,
    tools,
    get_yf_stock_info,
    get_yf_stock_history,
    get_yf_stock_recommendations,
)
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import streamlit as st
from collections import defaultdict

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # OpenRouter 전용 키

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",  # OpenRouter 사용
)


def tool_list_to_tool_obj(tools):
    """스트림으로 조각나서 들어오는 tool_calls 청크를 하나로 합쳐 리스트로 반환한다."""
    # 기본값을 가진 딕셔너리 초기화
    tool_calls_dict = defaultdict(
        lambda: {
            "id": None,
            "function": {"arguments": "", "name": None},
            "type": None,
        }
    )

    # 도구(함수) 호출을 반복하여 처리
    for tool_call in tools:
        if tool_call.id is not None:
            tool_calls_dict[tool_call.index]["id"] = tool_call.id

        if tool_call.function.name is not None:
            tool_calls_dict[tool_call.index]["function"]["name"] = tool_call.function.name

        # 인수 추가
        tool_calls_dict[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

        if tool_call.type is not None:
            tool_calls_dict[tool_call.index]["type"] = tool_call.type

    # 딕셔너리를 리스트로 변환
    tool_calls_list = list(tool_calls_dict.values())

    return {"tool_calls": tool_calls_list}


def get_ai_response(messages, tools=None, stream=True):
    response = client.chat.completions.create(
        model="openai/gpt-4o",  # OpenRouter 모델 형식
        stream=stream,          # (1) 스트리밍 출력을 위해 설정
        messages=messages,      # 대화 기록을 입력으로 전달
        tools=tools,            # 사용 가능한 도구 목록을 전달
    )

    if stream:
        for chunk in response:
            yield chunk  # 생성된 응답의 내용을 yield 로 순차적으로 반환
    else:
        return response


# ───────────────────────────────────────────────
# Streamlit 앱
# ───────────────────────────────────────────────
st.title("💬 주식 상담 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},
    ]

for msg in st.session_state.messages:
    if msg["role"] == "assistant" or msg["role"] == "user":  # assistant/user 메시지만
        st.chat_message(msg["role"]).write(msg["content"])


if user_input := st.chat_input():  # 사용자 입력 받기
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    ai_response = get_ai_response(st.session_state.messages, tools=tools)

    content = ""
    tool_calls = None  # tool_calls 초기화
    tool_calls_chunk = []  # tool_calls_chunk 초기화

    with st.chat_message("assistant"):
        placeholder = st.empty()
        for chunk in ai_response:
            content_chunk = chunk.choices[0].delta.content
            if content_chunk:
                content += content_chunk
                placeholder.markdown(content)
            if chunk.choices[0].delta.tool_calls:
                tool_calls_chunk += chunk.choices[0].delta.tool_calls

    tool_obj = tool_list_to_tool_obj(tool_calls_chunk)
    tool_calls = tool_obj["tool_calls"]

    if len(tool_calls) > 0 and tool_calls[0]["id"] is not None:
        # tool_calls 에서 function 정보만 모아서 출력
        tool_call_msg = [tool_call["function"] for tool_call in tool_calls]
        st.write(tool_call_msg)

    print("\n===========")
    print(content)
    print(tool_calls)

    # tool_calls 가 있으면 도구를 실행하고 결과를 메시지에 추가한다.
    if tool_calls and tool_calls[0]["id"] is not None:
        # 도구 호출을 요청한 assistant 메시지를 먼저 기록
        st.session_state.messages.append(
            {"role": "assistant", "content": content, "tool_calls": tool_calls}
        )

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]      # 실행할 함수명
            tool_call_id = tool_call["id"]                 # 함수 호출 아이디
            arguments = json.loads(tool_call["function"]["arguments"])  # 문자열을 딕셔너리로

            if tool_name == "get_current_time":
                func_result = get_current_time(timezone=arguments["timezone"])
            elif tool_name == "get_yf_stock_info":
                func_result = get_yf_stock_info(ticker=arguments["ticker"])
            elif tool_name == "get_yf_stock_history":
                func_result = get_yf_stock_history(
                    ticker=arguments["ticker"],
                    period=arguments["period"],
                )
            elif tool_name == "get_yf_stock_recommendations":
                func_result = get_yf_stock_recommendations(ticker=arguments["ticker"])
            else:
                func_result = "알 수 없는 도구입니다."

            # 도구 실행 결과를 tool 메시지로 기록
            st.session_state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": str(func_result),
                }
            )

        st.session_state.messages.append(
            {"role": "system", "content": "이제 주어진 결과를 바탕으로 답변할 차례다."}
        )

        # 도구 결과를 반영해 다시 응답 받기 (스트림)
        ai_response = get_ai_response(st.session_state.messages, tools=tools)

        content = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for chunk in ai_response:
                content_chunk = chunk.choices[0].delta.content
                if content_chunk:
                    content += content_chunk
                    placeholder.markdown(content)

    # 최종 AI 응답을 대화 기록에 추가
    st.session_state.messages.append({"role": "assistant", "content": content})
    print("AI\t: " + content)
