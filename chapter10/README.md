# 10장 · RAG(검색 증강 생성) 챗봇

문서를 청크로 나누어 벡터 DB(크로마)에 저장하고, 질문과 유사한 청크를 검색해
그 내용을 근거로 답변하는 RAG 챗봇 실습이다.

## 실습 파일

| 순서 | 파일 | 내용 |
|------|------|------|
| 1 | [rag_practice.ipynb](rag_practice.ipynb) | RAG 전체 흐름 실습 (PDF 로드 → 청킹 → 임베딩 → 크로마 DB → 검색 → 답변 → 질의 확장). **먼저 실행해 `chroma_store/`를 만든다.** |
| 2 | [retriever.py](retriever.py) | 저장된 크로마 DB를 로드해 리트리버·답변 체인·질의 확장 체인을 제공하는 모듈 |
| 3 | [rag.py](rag.py) | 스트림릿 RAG 챗봇 (질의 확장 → 검색 → 답변 스트리밍) |

## 실습 데이터

`data/` 폴더에 PDF를 넣는다. (용량이 커서 깃에는 올리지 않는다)

- 서울: https://urban.seoul.go.kr/view/html/PMNU5020400001?booksType=BK0300 → `data/2040_seoul_plan.pdf`
- 뉴욕: https://a860-gpp.nyc.gov/concern/parent/gx41mm584/file_sets/1z40kw69m

노트북은 `data/2040_seoul_plan.pdf`를 읽는다. 뉴욕 문서도 추가하려면
`all_splits.extend(...)`로 청크를 이어 붙이면 된다.

## 환경 준비

```powershell
pip install PyMuPDF pypdf langchain langchain_community langchain_chroma langchain_openai python-dotenv streamlit
```

### ⚠️ API 키 — 정식 OpenAI 키가 필요

임베딩(`text-embedding-3-large`)과 생성(`gpt-4o`)은 **OpenRouter가 아닌 정식
OpenAI API**를 호출한다. 프로젝트 루트 `.env`의 `OPENAI_API_KEY`에 정식 키
(`sk-proj-...`)를 넣어야 한다. (다른 장에서 쓰는 OpenRouter 키 `sk-or-...`로는
임베딩이 동작하지 않는다.)

```
OPENAI_API_KEY=sk-proj-...
```

## 실행 순서

```powershell
# 1) 노트북을 끝까지 실행해 벡터 DB(chroma_store/) 생성
#    rag_practice.ipynb 를 VS Code / Jupyter 로 열어 실행

# 2) 스트림릿 챗봇 실행
streamlit run chapter10/rag.py
```
