from get_function import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import streamlit as st

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages,
        tools=tools,
    )
    return response

st.title("💬 Chatbot")


messages = [
    {
        "role": "system",
        "content": (
            "너는 사용자를 도와주는 비서야. "
            "사용자가 현재 시간을 물어볼 때 어느 지역(타임존) 기준인지 명확하지 않으면, "
            "도구를 호출하지 말고 먼저 어느 지역 기준인지 사용자에게 되물어봐."
        )
    }
]
for msg in st.session_state:
    if msg["role"] == "assistant" or msg["role"] == "user":
        st.chat_message(msg["role"]).write(msg["content"])
    
if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    ai_response = get_ai_response(st.session_state.messages, tools=tools)
    ai_message = ai_response.choices[0].message
    print(ai_message)
    
    tool_clalls = ai_message.tool_calls
    if tool_clalls:
        for tool_call in tool_clalls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)
            
            if tool_name == "get_current_time":
                st.session_state.messages.append({
                    "role": "function",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": get_current_time(timezone=arguments.get("timezone")),
                })
        st.session_state.messages.append({"role": "assistant", "content": "이제 주어진 결과를 바탕으로 최종 답변을 생성할 수 있어."})
        ai_response = get_ai_response(st.session_state.messages, tools=tools)
        ai_message = ai_response.choices[0].message
    
    st.session_state.messages.append({"role": "assistant", "content": ai_message.content})
    
    print(f"AI\t: {ai_message.content}")
    st.chat_message("assistant").write(ai_message.content)

while True:
    user_input = input("사용자\t: ")  # \t는 tab을 의미

    if user_input == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    # 1차 호출: 모델이 필요하다고 판단하면 도구 호출을 요청한다.
    ai_response = get_ai_response(messages, tools=tools)
    ai_message = ai_response.choices[0].message
    tool_calls = ai_message.tool_calls

    if tool_calls:
        # 모델의 도구 호출 메시지를 먼저 대화에 추가한다.
        tool_name = tool_calls[0].function.name
        tool_call_id = tool_calls[0].id
        arguments = json.loads(tool_calls[0].function.arguments)
        messages.append(ai_message)  # tool 응답보다 먼저 tool_calls 메시지를 추가해야 함

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            if tool_name == "get_current_time":
                # 실제 함수를 실행하고 그 결과를 tool 메시지로 돌려준다.
                result = get_current_time(timezone=arguments.get("timezone"))
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

        # 2차 호출: 도구 실행 결과를 바탕으로 최종 답변을 생성한다.
        ai_response = get_ai_response(messages, tools=tools)
        ai_message = ai_response.choices[0].message

    messages.append(ai_message)

    content = ai_message.content or "(응답 없음)"
    print(f"AI\t: {content}")
