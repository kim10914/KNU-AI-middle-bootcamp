# 11장 · 로컬에서 딥시크-R1 모델 사용하기

올라마(Ollama)로 딥시크-R1 모델을 내 PC에 설치해 로컬에서 실행하고,
랭체인·스트림릿과 연결해 챗봇과 RAG를 만든다.

## 실습 파일

| 순서 | 파일 | 내용 |
|------|------|------|
| 1 | [deepseek_simple_chatbot.py](deepseek_simple_chatbot.py) | 딥시크-R1(올라마) + 랭체인 **CLI 챗봇** (스트리밍, `<think>` 제거) |
| 2 | [retriever.py](retriever.py) | 임베딩=OpenAI, 생성=딥시크-R1 인 **RAG 리트리버/체인** 모듈 |
| 3 | [rag_deepseek.py](rag_deepseek.py) | 딥시크 기반 **스트림릿 RAG 챗봇** (질의 확장 → 검색 → 답변) |

## 사전 준비

### 1) 올라마 설치 + 모델 내려받기

- https://ollama.com 에서 올라마 설치 (**설치 후 VS Code를 반드시 재시작**해야 `ollama` 명령이 잡힌다)
- 딥시크-R1 모델 내려받기. 실습 코드는 가볍고 빠른 **1.5B**를 기본으로 쓴다 (약 1.1GB):

```powershell
ollama pull deepseek-r1:1.5b
```

> GPU가 넉넉하면 `deepseek-r1:8b`(약 5.2GB)가 답변 품질이 더 좋다.
> 그때는 세 파일의 `ChatOllama(model=...)` 를 `deepseek-r1:8b` 로 바꾼다.
> 8B는 CPU로 돌리면 추론(Thinking) 과정 때문에 상당히 느리다.

> 딥시크-R1은 답변 전에 추론(Thinking) 과정을 거치며 `<think>...</think>` 로 함께 출력한다.
> 경량 모델 특성상 가끔 다른 언어(중국어 등)가 섞일 수 있다. 종료는 `Ctrl + D`.

### 2) 패키지 설치

```powershell
pip install langchain-ollama
```

의존성 충돌(`langchain-core ... incompatible`) 이 나면 아래처럼 재정렬한다.

```powershell
python -m pip uninstall langchain-ollama langchain-core langsmith -y
python -m pip install --upgrade langchain langchain-core langchain-community langchain-ollama langchain-openai langchain-chroma langgraph langsmith
```

### 3) 벡터 DB (RAG용)

`retriever.py`는 **chapter10에서 만든 `chapter10/chroma_store`를 재사용**한다.
먼저 [chapter10/rag_practice.ipynb](../chapter10/rag_practice.ipynb)를 끝까지 실행해
벡터 DB를 만들어 둔다. (임베딩은 정식 OpenAI 키가 필요 — 루트 `.env`의 `OPENAI_API_KEY`)

## 실행

```powershell
# CLI 챗봇
python chapter11/deepseek_simple_chatbot.py

# 스트림릿 RAG 챗봇
streamlit run chapter11/rag_deepseek.py
```

## GPT판(chapter10)과 달라진 점

- **생성 모델**: `ChatOpenAI(gpt-4o)` → 로컬 `ChatOllama(deepseek-r1:8b)`. 임베딩만 OpenAI를 쓴다.
- **답변 파싱**: 딥시크 출력에 `<think>` 추론 블록이 붙으므로 CLI 챗봇에서는 `</think>` 뒤 실제 답변만 저장한다.
- **문서 출처 표시**: 스트림릿에서 `st.expander`로 답변 근거가 된 청크의 출처·페이지를 함께 보여준다.
