import os
import glob
import shutil
import subprocess
import numpy as np
import torch
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# ffmpeg 자동 탐색: 책의 r"C:\ffmpeg\bin" 대신 winget 설치 경로를 찾아 PATH에 추가
if shutil.which("ffmpeg") is None:
    _pkgs = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Microsoft", "WinGet", "Packages")
    _hits = glob.glob(os.path.join(_pkgs, "Gyan.FFmpeg*", "**", "ffmpeg.exe"),
                      recursive=True)
    if _hits:
        os.environ["PATH"] = os.path.dirname(_hits[0]) + os.pathsep + os.environ["PATH"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_audio(path, sr=16000):
    # ffmpeg로 디코딩한 배열을 넘겨 torchcodec DLL 문제를 피한다.
    ffmpeg = shutil.which("ffmpeg")
    cmd = [ffmpeg, "-nostdin", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32).copy()
    return {"raw": audio, "sampling_rate": sr}


# 받아쓰기 함수
def whisper_stt(
    audio_file_path: str,
    output_file_path: str = "./output.csv"
):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-tiny"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True,   # 청크별로 타임스탬프 반환
        chunk_length_s=10,  # 입력 오디오 10초씩 나누기
        stride_length_s=2,  # 2초씩 겹치도록 청크 나누기
    )

    result = pipe(load_audio(audio_file_path))
    df = whisper_to_dataframe(result, output_file_path)
    return result, df


def whisper_to_dataframe(result, output_file_path):
    start_end_text = []
    for chunk in result["chunks"]:
        start = chunk["timestamp"][0]
        end = chunk["timestamp"][1]
        text = chunk["text"]
        start_end_text.append([start, end, text])
        df = pd.DataFrame(start_end_text, columns=["start", "end", "text"])
        df.to_csv(output_file_path, index=False, sep=":")
    return df


if __name__ == "__main__":
    result, df = whisper_stt(
        os.path.join(BASE_DIR, "audio", "싼기타_비싼기타.mp3"),
        os.path.join(BASE_DIR, "audio", "싼기타_비싼기타.csv"),
    )
    print(df)
