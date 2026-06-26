import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
api_key = os.getenv("OPEN_API_KEY")
if not api_key:
    raise RuntimeError("venv/.env 파일에 OPEN_API_KEY를 설정하세요.")

print(api_key[:12] + "...")
response = requests.get(
    "https://openrouter.ai/api/v1/key",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)
if response.status_code != 200:
    print("status:", response.status_code)
    print("body:", response.text)
    raise RuntimeError("OpenRouter 인증 실패")
data = response.json()["data"]
print(f"키 이름: {data.get('label')}")
print(f"총 한도: ${data.get('limit')}")
print(f"사용 금액: ${data.get('usage')}")
print(f"남은 금액: ${data.get('limit_remaining')}")
