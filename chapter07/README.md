# chapter07 — 랭체인으로 에이전트 만들기

7장 슬라이드 실습 코드입니다. OpenRouter 경유로 `openai/gpt-4o-mini` 모델을 사용합니다.

## 설치

```bash
pip install langchain langchain-openai langchain-core python-dotenv pytz yfinance streamlit tabulate
```

> `agent_tools.py` 의 `history.to_markdown()` 는 `tabulate` 패키지가 필요합니다.

`.env` 에 `OPENAI_API_KEY` (OpenRouter 키) 가 설정되어 있어야 합니다.

## 파일 구성 (슬라이드 순서)

데모는 주피터 노트북(`.ipynb`), 스트림릿 앱은 파이썬 스크립트(`.py`)입니다.

### 노트북 — VS Code / Jupyter 로 셀을 위에서 아래로 실행

| 파일 | 내용 |
| --- | --- |
| `langchain_basic.ipynb` | 랭체인 기본 챗봇 (단발성 호출, 기억 못 함) |
| `langchain_multi_turn.ipynb` | 메시지 리스트로 멀티턴 (입력창에 `exit` 로 종료) |
| `message_history.ipynb` | 세션별 메시지 히스토리 + 스트림 |
| `lcel_chain.ipynb` | LCEL 체인 · 프롬프트 템플릿 · 구조화 출력(파이단틱) |
| `agent_tools.ipynb` | 도구로 에이전트 만들기 · 파이단틱 입력 · 스트림 |

### 스트림릿 앱 — `streamlit run` 으로 실행

| 파일 | 내용 | 실행 |
| --- | --- | --- |
| `chatbot_memory.py` | 스트림릿 챗봇 (메시지 히스토리 메모리) | `streamlit run chapter07/chatbot_memory.py` |
| `chatbot_no_memory.py` | 스트림릿 챗봇 (메모리 없이 멀티턴) | `streamlit run chapter07/chatbot_no_memory.py` |
| `chatbot_tools.py` | 스트림릿 챗봇 (도구 추가 + 스트림) | `streamlit run chapter07/chatbot_tools.py` |

## 참고

- `message_history.py` / `chatbot_memory.py` 의 `RunnableWithMessageHistory` 는
  최신 랭체인에서 deprecated 경고가 날 수 있으나, 책의 흐름을 따라 그대로 사용합니다.
