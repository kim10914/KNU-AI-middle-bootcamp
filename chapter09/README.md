# 9장 · 음성을 텍스트로 정리하기

녹음된 음성을 텍스트로 바꾸고(STT), 화자를 구분해 회의록 형태로 정리하는 실습이다.

## 실습 파일

| 순서 | 파일 | 내용 |
|------|------|------|
| 1 | [1_whisper_api.ipynb](1_whisper_api.ipynb) | 위스퍼 **API**로 받아쓰기 + 영어 번역 (OpenAI 크레딧 필요) |
| 2 | [2_huggingface_whisper.ipynb](2_huggingface_whisper.ipynb) | **로컬** 위스퍼(HuggingFace)로 받아쓰기 → CSV 저장 |
| 3 | [3_pyannote_diarization.ipynb](3_pyannote_diarization.ipynb) | **화자 분리**(pyannote) → RTTM → 화자별 CSV로 정리 |
| 4 | [4_whisper_stt.py](4_whisper_stt.py) | 받아쓰기 + 화자 분리를 **함수화**한 통합 스크립트 |
| 5 | [5_summarize.ipynb](5_summarize.ipynb) | 받아쓴 대화록을 **GPT(gpt-4o)로 요약** |

`audio/` 에 실습용 음성 파일이 있다. (`lsy_audio_2023_58s.mp3` 1인 / `싼기타_비싼기타.mp3` 2인)

## 환경 준비

```powershell
# 1) 패키지
pip install torch==2.11.0 torchvision==0.26.0 torchaudio==2.11.0
pip install transformers accelerate pandas openai python-dotenv pyannote.audio

# 2) ffmpeg (mp3 디코딩에 필수)
winget install Gyan.FFmpeg

# 3) torchcodec 제거 (Windows에서 오디오 디코딩을 깨뜨림 — 아래 4번 참고)
pip uninstall -y torchcodec
```

`.env` 파일(프로젝트 루트)에 키를 둔다.

```
OPENAI_DIRECT_KEY=sk-proj-...      # 1번(위스퍼 API)용 OpenAI 정식 키
HUGGINGFACE_API_KEY=hf_...          # 3번(화자 분리)용 HF Read 토큰
```

## 이 환경에서 책과 달라진 점 (중요)

책 예제를 그대로 쓰면 이 PC에서는 오류가 나서, 아래를 반영했다.

1. **torch 버전 고정** — `torch 2.11.0 / torchvision 0.26.0 / torchaudio 2.11.0`.
   버전이 어긋나면 `RuntimeError: operator torchvision::nms does not exist` 발생.
2. **ffmpeg 자동 탐색** — 책의 `r"C:\ffmpeg\bin"` 대신, winget 설치 경로를
   코드에서 자동으로 찾아 PATH에 추가한다. (터미널 재시작 불필요)
3. **오디오 디코딩(torchcodec 제거)** — 최신 pyannote/transformers는 torchcodec으로
   오디오를 읽는데, Windows에서 ffmpeg DLL 문제로 실패한다(`libtorchcodec_core*.dll`).
   torchcodec을 제거하고, 모든 코드는 ffmpeg로 직접 디코딩한 배열/파형을 넘겨 우회한다.
   (torchaudio·pyannote 재설치 시 torchcodec이 다시 깔릴 수 있으니 그때는 다시 제거)
4. **결과 객체 변경** — 최신 pyannote는 `DiarizeOutput`을 반환하므로
   `output.speaker_diarization` 에서 기존 Annotation(itertracks/write_rttm)을 꺼낸다.

## 화자 분리(3번) 게이트 모델 동의

pyannote 3.1은 아래 세 모델의 약관 동의가 필요하다. HF 로그인 후 각 페이지에서
"Agree and access repository"를 누른다.

- https://hf.co/pyannote/speaker-diarization-3.1
- https://hf.co/pyannote/segmentation-3.0
- https://hf.co/pyannote/speaker-diarization-community-1
