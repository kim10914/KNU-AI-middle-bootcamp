"""② PDF 의 헤더와 푸터는 제외하고 읽기 (전처리)

페이지 상단(헤더)과 하단(푸터) 영역을 잘라내고 본문 영역의 텍스트만 추출한다.
전처리가 잘 되어 있으면 비싼 모델(gpt-4o) 대신 저렴한 모델로도 좋은 요약을 얻을 수 있다.
"""

import os
import pymupdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

pdf_file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축.pdf")
doc = pymupdf.open(pdf_file_path)

# 잘라낼 헤더/푸터 높이 (PDF 좌표 단위, pt). 문서에 맞게 조절
header_height = 80
footer_height = 80

full_text = ""

for page in doc:
    rect = page.rect  # 페이지 크기 가져오기

    # 헤더/푸터 영역의 텍스트 (확인용으로 따로 추출)
    header = page.get_text(clip=(0, 0, rect.width, header_height))
    footer = page.get_text(clip=(0, rect.height - footer_height, rect.width, rect.height))

    # 본문 영역(헤더/푸터 제외)의 텍스트만 추출
    text = page.get_text(clip=(0, header_height, rect.width, rect.height - footer_height))

    full_text += text + "\n------------------------------------\n"

# 전처리된 결과는 _pre 를 붙여 별도 저장
txt_file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축_pre.txt")
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"전처리 텍스트 추출 완료: {txt_file_path}")
