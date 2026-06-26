"""① PDF 에서 텍스트 추출하기 (기본)

PyMuPDF(pymupdf) 로 PDF 의 모든 페이지에서 텍스트를 추출해 .txt 로 저장한다.
이 방식은 본문뿐 아니라 페이지 번호, 헤더, 푸터까지 함께 추출된다는 한계가 있다.
→ 전처리는 pdf_to_text_pre.py 참고
"""

import os
import pymupdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ① PDF 파일 경로 지정 및 불러오기
pdf_file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축.pdf")
doc = pymupdf.open(pdf_file_path)

full_text = ""

# ② 문서의 각 페이지를 순회하며 텍스트 추출 및 병합
for page in doc:                  # 문서 페이지 반복
    text = page.get_text()        # 페이지 텍스트 추출
    full_text += text

# ③ 추출한 텍스트를 파일로 저장
txt_file_path = os.path.join(DATA_DIR, "과정기반 작물모형을 이용한 구축.txt")
with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"텍스트 추출 완료: {txt_file_path}")
