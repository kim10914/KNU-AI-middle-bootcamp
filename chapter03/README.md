# chapter03 — 논문을 요약해 주는 AI 연구원

PDF 논문을 텍스트로 변환·전처리한 뒤, GPT 로 정해진 포맷에 맞게 요약하는 실습입니다.

## 📦 준비

```bash
pip install pymupdf openai python-dotenv
```

루트의 `.env` 에 `OPENAI_API_KEY`(OpenRouter 키)가 설정되어 있어야 합니다.

요약할 PDF 파일을 `chapter03/data/` 폴더에 넣으세요. 기본 코드는
`과정기반 작물모형을 이용한 구축.pdf` 라는 이름을 가정하므로, 다른 파일을 쓰려면
각 스크립트의 `pdf_file_path` 를 수정하면 됩니다.

> 실습용 PDF 는 저작권 문제로 저장소에 포함하지 않습니다.
> 예제는 한국농공학회(kase.re.kr) 논문집 2024년 4호의
> '과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축' 논문을 사용했습니다.

## 📂 파일 구성 (실습 진행 순서)

| 파일 | 설명 |
| --- | --- |
| `pdf_to_text.py` | ① PDF 전체 텍스트 추출 (헤더·푸터 포함, 한계 확인용) |
| `pdf_to_text_pre.py` | ② 헤더·푸터를 제외하고 본문만 추출 (전처리) |
| `summarize_txt.py` | ③ 전처리된 텍스트를 정해진 포맷으로 요약 |
| `summarize_pdf.py` | ④ PDF 입력 → 추출 → 요약 → 저장까지 한 번에 (완성본) |

## ▶️ 실행

```bash
python chapter03/pdf_to_text.py        # ①
python chapter03/pdf_to_text_pre.py    # ②
python chapter03/summarize_txt.py      # ③
python chapter03/summarize_pdf.py      # ④ (완성본)
```

## 💡 핵심 포인트

- PDF 를 그대로 텍스트로 바꾸면 페이지 번호·학회지명·논문 제목 등 헤더/푸터가 본문에 섞입니다.
- `page.get_text(clip=...)` 로 상·하단 영역을 잘라내면 본문만 깔끔하게 추출됩니다.
- 전처리 품질이 좋을수록 저렴한 모델로도 충분히 좋은 요약을 얻을 수 있습니다.
