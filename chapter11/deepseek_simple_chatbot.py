"""딥시크-R1(올라마)과 랭체인으로 만든 CLI 챗봇.

올라마로 로컬에 받은 deepseek-r1 모델을 ChatOllama로 불러 대화한다.
답변이 한 번에 나오면 느리므로 stream()으로 토큰을 실시간 출력한다.

사전 준비:
  1) https://ollama.com 에서 올라마 설치 (설치 후 VS Code 재시작)
  2) 터미널에서 모델 내려받기:  ollama run deepseek-r1:1.5b
  3) pip install langchain-ollama

실행:  python chapter11/deepseek_simple_chatbot.py   (종료: exit)
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatOllama(model="deepseek-r1:8b")

messages = [
    SystemMessage("너는 사용자를 도와주는 상담사야."),
]

while True:
    user_input = input("사용자: ")

    if user_input == "exit":
        break

    messages.append(HumanMessage(user_input))

    # 답변이 스트림 방식으로 출력되도록 한다.
    response = llm.stream(messages)
    ai_message = None
    print("AI: ", end="")
    for chunk in response:
        print(chunk.content, end="", flush=True)
        if ai_message is None:
            ai_message = chunk
        else:
            ai_message += chunk
    print("")

    # 딥시크-R1은 <think>...</think> 로 추론 과정을 함께 출력하므로,
    # </think> 뒤의 실제 답변만 대화 기록에 저장한다.
    if "</think>" in ai_message.content:
        message_only = ai_message.content.split("</think>")[1].strip()
    else:
        message_only = ai_message.content
    messages.append(AIMessage(message_only))
