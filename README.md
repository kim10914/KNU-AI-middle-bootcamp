# KNU AI 부트캠프 (중급)

경북대학교 AI 중급 부트캠프 실습 자료 저장소입니다.
OpenRouter API를 이용해 LLM·이미지 관련 실습을 진행합니다.

## 📁 폴더 구조

```
.
├── chapter01/          # OpenRouter / GPT 기본 호출
│   ├── gpt_basic.py    # openai SDK로 채팅 완성 호출
│   └── free.py         # API 키 잔액·한도 조회
├── chapter02/          # (작업 예정)
├── chapter03/          # 이미지 관련 실습
│   ├── hello.ipynb
│   ├── image.ipynb
│   ├── ju_image.ipynb
│   └── data/images/    # 실습용 이미지
├── .env.example        # 환경변수 템플릿 (복사해서 .env로 사용)
├── .gitignore
└── README.md
```

## ⚙️ 환경 설정

### 1. 가상환경 생성 및 활성화

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install openai requests python-dotenv
```

### 3. 환경변수 설정

`.env.example`을 복사해 `.env`를 만들고 본인의 OpenRouter API 키를 넣으세요.

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# macOS / Linux
cp .env.example .env
```

`.env` 파일 내용:

```
OPEN_API_KEY=sk-or-본인_키
OPENAI_API_KEY=sk-or-본인_키
```

> ⚠️ `.env`는 `.gitignore`에 등록되어 있어 깃에 올라가지 않습니다. **API 키를 코드에 직접 쓰거나 커밋하지 마세요.**

## ▶️ 실행 방법

```bash
# 파이썬 스크립트
python chapter01/gpt_basic.py
python chapter01/free.py

# 노트북은 VS Code 또는 Jupyter로 열어서 실행
```

## 🔑 API 키 발급

[OpenRouter](https://openrouter.ai/keys)에서 무료로 키를 발급받을 수 있습니다.
