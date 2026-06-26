"""③ 텍스트 파일 읽고 요약하기

전처리된 텍스트 파일을 읽어, 정해진 포맷(제목 / 문제 인식·주장 / 저자 소개)으로
요약해 주는 함수. OpenRouter 를 통해 OpenAI 모델을 호출한다.
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Windows 콘솔(cp949)에서 한글·특수문자 출력 시 인코딩 에러 방지
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def summarize_txt(file_path: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # ② 주어진 텍스트 파일을 읽어들인다.
    with open(file_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # ③ 요약을 위한 시스템 프롬프트를 생성한다.
    system_prompt = f"""너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라.

작성해야 하는 포맷은 다음과 같다.

# 제목

## 저자의 문제 인식 및 주장 (15문장 이내)

## 저자 소개


=============== 이하 텍스트 ===============

{txt}
"""

    print(system_prompt)
    print("=========================================")

    # ④ OpenAI API를 사용하여 요약을 생성한다.
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # 실제 전처리된 텍스트 파일 경로
    file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축_pre.txt")

    summary = summarize_txt(file_path)
    print(summary)

    # ⑤ 요약된 내용을 파일로 저장한다.
    output_file_path = os.path.join(DATA_DIR, "summary.txt")
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(summary)
