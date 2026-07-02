"""크로마 DB와 임베딩 모델을 활용한 질의응답(RAG) 시스템.

rag.py(스트림릿 앱)에서 `import retriever` 로 불러 쓴다.
미리 만들어 둔 크로마 DB(./chroma_store)를 로드해서
- retriever         : 유사 청크 검색기
- document_chain    : 검색한 청크(context)를 근거로 답변 생성
- query_augmentation_chain : 모호한 질문을 명확한 한 문장으로 확장
를 제공한다.
"""

import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
try:
    # langchain 1.x: classic 체인은 langchain_classic 으로 이동
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
except ModuleNotFoundError:
    from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser  # 문자열 출력 파서

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ── 임베딩 모델 선언하기 ────────────────────────────────────────
embedding = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)

# ── 언어 모델 불러오기 ──────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

# ── 저장된 크로마 DB 로드 ───────────────────────────────────────
# build_db.ipynb 에서 미리 만들어 둔 벡터 DB 를 불러온다.
print("Loading existing Chroma store")
persist_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_store")

vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding,
)

# ── 리트리버 만들기 ─────────────────────────────────────────────
# 질문과 가장 유사한 청크 k개를 가져온다.
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
document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

# ── 질의 확장(query augmentation) 체인 ──────────────────────────
# 기존 대화 내용을 활용해 모호한 질문을 명확한 한 문장으로 변환한다.
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
