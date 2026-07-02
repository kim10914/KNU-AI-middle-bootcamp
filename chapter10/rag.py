"""스트림릿으로 완성한 RAG 챗봇.

retriever.py 가 미리 만들어 둔 크로마 DB / 체인을 불러 쓴다.
1) 사용자가 질문하면 → 질의 확장으로 질문을 명확하게 다듬고
2) 리트리버로 관련 청크를 검색한 뒤
3) 그 청크(context)를 근거로 답변을 생성한다.

실행: streamlit run chapter10/rag.py
"""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

import retriever  # 위에서 만든 리트리버/체인 모듈

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_ai_response(messages, docs):
    """검색한 청크(docs)를 근거로 답변을 스트리밍으로 생성한다."""
    response = retriever.document_chain.stream(
        {
            "messages": messages,
            "context": docs,
        }
    )
    for chunk in response:
        yield chunk  # create_stuff_documents_chain 은 문자열 청크를 반환


# ── Streamlit 앱 ────────────────────────────────────────────────
st.title("💬 GPT-4o 랭체인 RAG 챗봇")

# 스트림릿 session_state에 메시지 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 문서에 기반해 답변하는 도시 정책 전문가야.")
    ]

# 스트림릿 화면에 이전 메시지 출력
for msg in st.session_state.messages:
    if msg.content:
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        # SystemMessage는 출력하지 않음

# 사용자 입력 처리
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(HumanMessage(prompt))

    # 1) 질의 확장 — 대화 맥락을 반영해 질문을 명확하게 다듬는다.
    augmented_query = retriever.query_augmentation_chain.invoke(
        {
            "messages": st.session_state["messages"],
            "query": prompt,
        }
    )
    augmented_query = str(augmented_query)
    print("augmented_query\t", augmented_query)

    # 2) 관련 문서 검색 — 원 질문 + 확장된 질문으로 유사 청크를 가져온다.
    print("관련 문서 검색")
    docs = retriever.retriever.invoke(f"{prompt}\n{augmented_query}")
    for doc in docs:
        print("--------------------------")
        print(doc)
    print("==========================")

    # 3) 청크를 근거로 답변 생성 (스트리밍)
    with st.chat_message("assistant"):
        result = st.write_stream(get_ai_response(st.session_state["messages"], docs))

    st.session_state["messages"].append(AIMessage(result))
