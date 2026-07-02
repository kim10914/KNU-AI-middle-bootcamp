"""딥시크(올라마) 기반 RAG의 리트리버/체인 모듈.

임베딩은 OpenAI(text-embedding-3-large), 생성은 로컬 딥시크-R1(ChatOllama)을 쓴다.
벡터 DB는 chapter10에서 만들어 둔 chroma_store 를 재사용한다.
(chapter10/rag_practice.ipynb 를 먼저 끝까지 실행해 chroma_store 를 만들어 둘 것)
"""

import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser  # 문자열 출력 파서

try:
    # langchain 1.x: classic 체인은 langchain_classic 으로 이동
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
except ModuleNotFoundError:
    from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ── 임베딩 모델 선언하기 (OpenAI) ───────────────────────────────
embedding = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)

# ── 언어 모델 불러오기 (로컬 딥시크-R1) ─────────────────────────
llm = ChatOllama(model="deepseek-r1:8b")

# ── 저장된 크로마 DB 로드 (chapter10 의 것 재사용) ──────────────
print("Loading existing Chroma store")
_here = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(_here, "..", "chapter10", "chroma_store")

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding,
)

# ── 리트리버 만들기 ─────────────────────────────────────────────
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ── 검색한 청크(context)를 근거로 답변하는 체인 ─────────────────
question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "사용자의 질문에 대해 아래 context에 기반하여 답변하라.:\n\n{context}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
# 딥시크 답변을 바로 문자열로 받도록 StrOutputParser 를 연결한다.
document_chain = create_stuff_documents_chain(llm, question_answering_prompt) | StrOutputParser()

# ── 질의 확장(query augmentation) 체인 ──────────────────────────
query_augmentation_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),  # 기존 대화 내용
        (
            "system",
            "기존의 대화 내용을 활용하여 사용자의 아래 질문의 의도를 파악하여 "
            "명료한 한 문장의 질문으로 변환하라. 대명사나 이, 저, 그와 같은 표현을 "
            "명확한 명사로 바꾸어라.",
        ),
    ]
)
query_augmentation_chain = query_augmentation_prompt | llm | StrOutputParser()
