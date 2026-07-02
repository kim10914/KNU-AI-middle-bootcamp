"""딥시크(올라마)에 기반한 스트림릿 RAG 챗봇.

retriever.py 가 만들어 둔 리트리버/체인(임베딩=OpenAI, 생성=딥시크-R1)을 불러 쓴다.
질의 확장 → 관련 문서 검색 → 검색한 청크를 근거로 답변(스트리밍)한다.

실행: streamlit run chapter11/rag_deepseek.py
"""

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

import retriever  # 위에서 만든 리트리버/체인 모듈

# 모델 초기화
llm = ChatOllama(model="deepseek-r1:8b")


def get_ai_response(messages, docs):
    """검색한 청크(docs)를 근거로 답변을 스트리밍으로 생성한다."""
    response = retriever.document_chain.stream(
        {
            "messages": messages,
            "context": docs,
        }
    )
    for chunk in response:
        yield chunk  # StrOutputParser 를 거쳐 문자열 청크가 나온다


# ── Streamlit 앱 ────────────────────────────────────────────────
st.title("💬 DeepSeek-R1 랭체인 RAG 챗봇")

# 스트림릿 session_state에 메시지 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 문서에 기반해 답변하는 도시 정책 전문가야."),
        AIMessage("무엇을 도와드릴까요?"),
    ]

# 스트림릿 화면에 이전 메시지 출력
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
    st.chat_message("user").write(prompt)  # 사용자 메시지 출력
    st.session_state.messages.append(HumanMessage(prompt))  # 사용자 메시지 저장

    # 1) 질의 확장 — 대화 맥락을 반영해 질문을 명확하게 다듬는다.
    augmented_query = retriever.query_augmentation_chain.invoke(
        {
            "messages": st.session_state["messages"],
            "query": prompt,
        }
    )
    print("augmented_query\t", augmented_query)

    # 2) 관련 문서 검색 — 원 질문 + 확장된 질문으로 유사 청크를 가져온다.
    print("관련 문서 검색")
    docs = retriever.retriever.invoke(f"{prompt}\n{augmented_query}")

    for doc in docs:
        print("----------------")
        print(doc)
        with st.expander(f"**문서:** {doc.metadata.get('source', '알 수 없음')}"):
            # 파일명과 페이지 정보 표시
            st.write(f"**page:** {doc.metadata.get('page', '')}")
            st.write(doc.page_content)
    print("================")

    # 3) 청크를 근거로 답변 생성 (스트리밍)
    with st.spinner(f"AI가 답변을 준비 중입니다... '{augmented_query}'"):
        response = get_ai_response(st.session_state["messages"], docs)
        result = st.chat_message("assistant").write_stream(response)  # AI 메시지 출력

    st.session_state["messages"].append(AIMessage(result))  # AI 메시지 저장
