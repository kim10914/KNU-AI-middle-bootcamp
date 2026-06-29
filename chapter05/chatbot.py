"""Streamlit 웹 챗봇 (스트림 출력 + 함수 호출 / tool use 예제)

실행: streamlit run chapter05/chatbot.py

이 챗봇이 하는 일
- GPT가 필요하다고 판단하면 아래 4개의 도구(함수)를 직접 호출한다.
    · get_current_time            : 특정 지역의 현재 시각
    · get_yf_stock_info           : 종목 기본 정보
    · get_yf_stock_history        : 최근 주가 이력
    · get_yf_stock_recommendations: 애널리스트 추천 정보
- stream=True 로 응답을 '조각(chunk)' 단위로 받아 타이핑하듯 출력한다.
- 대화 기록은 st.session_state 에 보관해, 입력마다 스크립트가 재실행돼도 이어진다.
"""

from collections import defaultdict
from get_function import (
    get_current_time,
    get_yf_stock_info,
    get_yf_stock_history,
    get_yf_stock_recommendations,
    tools,
)
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import streamlit as st

load_dotenv()  # .env 파일의 환경변수 로드
api_key = os.getenv("OPENAI_API_KEY")  # 환경변수에서 API 키 가져오기

client = OpenAI(  # OpenAI 클라이언트 생성 (OpenRouter 경유)
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

SYSTEM_PROMPT = "너는 사용자를 도와주는 비서야."


def get_ai_response(messages, tools=None, stream=True):
    """GPT 응답을 생성한다.

    stream=True 이면 완성된 답변을 한 번에 받지 않고, 생성되는 즉시
    조각(chunk) 단위로 흘려보낸다(yield). 덕분에 ChatGPT처럼 글자가
    타이핑되듯 출력할 수 있다.

    주의: 이 함수는 yield 를 포함하므로 '제너레이터'다. 따라서 호출 결과는
    항상 for 문 등으로 '순회'해서 사용해야 한다. (response.choices[0]... 식으로
    바로 접근하면 'generator' object has no attribute 'choices' 오류가 난다)
    """
    response = client.chat.completions.create(
        model="openai/gpt-4o",  # 응답 생성에 사용할 모델
        messages=messages,      # 지금까지의 대화 기록
        tools=tools,            # 사용 가능한 도구 목록
        stream=stream,          # 스트리밍 출력 여부
    )
    for chunk in response:
        yield chunk  # 조각 하나를 호출한 쪽으로 순차적으로 넘겨준다.


def tool_list_to_tool_obj(tool_call_chunks):
    """스트림으로 조각조각 도착한 함수 호출 정보를 하나로 합친다.

    stream=True 일 때는 함수 호출(tool call) 정보도 여러 조각으로 쪼개져 온다.
    예를 들어 함수 이름은 첫 조각에만, arguments 는 글자 단위로 나뉘어 도착한다.
        조각1: name='get_current_time', arguments=''
        조각2: name=None,               arguments='{"'
        조각3: name=None,               arguments='timezone'
        ...
    이 조각들을 index(몇 번째 함수 호출인지) 기준으로 모아, 완성된
    tool_calls 리스트로 되돌리는 함수다.
    """
    # index 별로 기본 골격을 자동 생성해 주는 딕셔너리 (없는 키를 접근하면 lambda 실행)
    tool_calls_dict = defaultdict(
        lambda: {
            "id": None,
            "function": {"arguments": "", "name": None},
            "type": None,
        }
    )

    for tool_call in tool_call_chunks:
        # id 는 첫 조각에만 들어오므로 None 이 아닐 때만 저장
        if tool_call.id is not None:
            tool_calls_dict[tool_call.index]["id"] = tool_call.id

        # 함수 이름도 첫 조각에만 들어옴
        if tool_call.function.name is not None:
            tool_calls_dict[tool_call.index]["function"]["name"] = tool_call.function.name

        # arguments 는 글자 단위로 쪼개져 오므로 계속 이어붙인다.
        if tool_call.function.arguments is not None:
            tool_calls_dict[tool_call.index]["function"]["arguments"] += tool_call.function.arguments

        # 타입(function) 정보도 None 이 아닐 때만 저장
        if tool_call.type is not None:
            tool_calls_dict[tool_call.index]["type"] = tool_call.type

    # index 순서대로 리스트로 변환해 반환
    tool_calls_list = list(tool_calls_dict.values())
    return {"tool_calls": tool_calls_list}


def stream_ai_message(ai_response):
    """스트림 응답을 화면에 타이핑하듯 출력하며, 본문과 함수 호출 조각을 모은다.

    반환값: (content, tool_calls)
        content    : 합쳐진 답변 텍스트
        tool_calls : 완성된 함수 호출 리스트(없으면 빈 리스트)
    """
    content = ""              # 답변 본문을 누적할 변수
    tool_call_chunks = []     # 함수 호출 조각을 모을 리스트

    # .empty() 컨테이너는 내용을 매번 '교체'한다 → 누적 텍스트를 다시 그리면 타이핑 효과
    with st.chat_message("assistant").empty():
        for chunk in ai_response:
            delta = chunk.choices[0].delta

            content_chunk = delta.content
            if content_chunk:  # 본문 조각이 있으면
                content += content_chunk
                st.markdown(content)  # 지금까지 모인 내용을 다시 그림

            if delta.tool_calls:  # 함수 호출 조각이 있으면 따로 모아둔다
                tool_call_chunks += delta.tool_calls

    # 조각난 함수 호출 정보를 완성된 형태로 합친다.
    tool_calls = tool_list_to_tool_obj(tool_call_chunks)["tool_calls"]
    return content, tool_calls


st.title("💬 Chatbot")

# 대화 기록 초기화 (최초 1회만). Streamlit 은 입력마다 스크립트를 다시 실행하므로
# 일반 변수가 아닌 session_state 에 저장해야 대화가 이어진다.
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 이전 대화 다시 그리기 (system / tool 메시지는 화면에 표시하지 않음)
for msg in st.session_state.messages:
    if msg["role"] in ("assistant", "user") and msg.get("content"):
        st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 처리
if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 1차 응답: 스트림으로 받아 화면에 출력하면서 본문/함수 호출 조각을 모은다.
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    content, tool_calls = stream_ai_message(ai_response)

    # 함수 호출이 있으면 실제로 함수를 실행한다.
    if len(tool_calls) > 0:
        # tool 결과보다 먼저, 함수 호출을 요청한 assistant 메시지를 기록해야 한다.
        # (OpenAI 규칙: role="tool" 메시지는 tool_calls 를 가진 assistant 뒤에 와야 함)
        st.session_state.messages.append({
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        })

        for tool_call in tool_calls:
            # 스트림에서 합친 결과는 '딕셔너리' 형태이므로 키로 접근한다.
            tool_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]
            arguments = json.loads(tool_call["function"]["arguments"])  # 문자열 → 딕셔너리

            # 어떤 함수를 호출해야 하는지 이름으로 분기한다.
            if tool_name == "get_current_time":
                func_result = get_current_time(timezone=arguments.get("timezone"))
            elif tool_name == "get_yf_stock_info":
                func_result = get_yf_stock_info(ticker=arguments.get("ticker"))
            elif tool_name == "get_yf_stock_history":
                func_result = get_yf_stock_history(
                    ticker=arguments.get("ticker"),
                    period=arguments.get("period"),
                )
            elif tool_name == "get_yf_stock_recommendations":
                func_result = get_yf_stock_recommendations(ticker=arguments.get("ticker"))
            else:
                func_result = "지원하지 않는 함수입니다."

            # 함수 실행 결과를 tool 메시지로 기록한다.
            st.session_state.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": func_result,
            })

        # 함수 결과를 바탕으로 GPT가 최종 답변을 만들도록 다시 요청한다.
        st.session_state.messages.append(
            {"role": "system", "content": "이제 주어진 결과를 바탕으로 답변할 차례다."}
        )
        ai_response = get_ai_response(st.session_state.messages, tools=tools)
        content, _ = stream_ai_message(ai_response)

    # 최종 답변을 대화 기록에 저장한다.
    st.session_state.messages.append({"role": "assistant", "content": content})
