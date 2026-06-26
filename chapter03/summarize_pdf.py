"""④ 논문을 요약해 주는 AI 연구원 완성하기

PDF 파일만 입력하면 ① 헤더/푸터를 제외한 텍스트 추출 → ② 요약 → ③ 저장까지
한 번에 처리하는 완성본.
"""

import os
import sys
import pymupdf
from openai import OpenAI
from dotenv import load_dotenv

# Windows 콘솔(cp949)에서 한글·특수문자 출력 시 인코딩 에러 방지
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def pdf_to_text(pdf_file_path: str):
    """헤더/푸터를 제외하고 PDF 본문 텍스트를 추출해 .txt 로 저장하고 경로를 반환한다."""
    doc = pymupdf.open(pdf_file_path)
    header_height = 80
    footer_height = 80
    full_text = ""

    for page in doc:
        rect = page.rect  # 페이지 크기 가져오기
        header = page.get_text(clip=(0, 0, rect.width, header_height))
        footer = page.get_text(clip=(0, rect.height - footer_height, rect.width, rect.height))
        text = page.get_text(clip=(0, header_height, rect.width, rect.height - footer_height))
        full_text += text + "\n------------------------------------\n"

    txt_file_path = os.path.splitext(pdf_file_path)[0] + "_pre.txt"
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return txt_file_path


def summarize_txt(file_path: str):
    """텍스트 파일을 읽어 정해진 포맷으로 요약한 결과를 반환한다."""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    with open(file_path, "r", encoding="utf-8") as f:
        txt = f.read()

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

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
        ],
    )

    return response.choices[0].message.content


def summarize_pdf(pdf_file_path: str, output_file_path: str):
    """PDF → 텍스트 추출 → 요약 → 파일 저장까지 한 번에 처리한다."""
    txt_file_path = pdf_to_text(pdf_file_path)
    summary = summarize_txt(txt_file_path)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    pdf_file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축.pdf")
    output_file_path = os.path.join(DATA_DIR, "summary2.txt")

    summarize_pdf(pdf_file_path, output_file_path)
    print("PDF 텍스트 추출 및 요약본 저장이 모두 완료되었습니다.")
