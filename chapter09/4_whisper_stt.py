import os
import glob
import shutil
import subprocess
import numpy as np
import torch
import pandas as pd
from dotenv import load_dotenv
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline

load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ffmpeg 자동 탐색: 책의 r"C:\ffmpeg\bin" 대신 winget 설치 경로를 찾아 PATH에 추가
if shutil.which("ffmpeg") is None:
    _pkgs = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Microsoft", "WinGet", "Packages")
    _hits = glob.glob(os.path.join(_pkgs, "Gyan.FFmpeg*", "**", "ffmpeg.exe"),
                      recursive=True)
    if _hits:
        os.environ["PATH"] = os.path.dirname(_hits[0]) + os.pathsep + os.environ["PATH"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def decode_audio(path, sr=16000):
    """ffmpeg로 오디오를 mono float32 배열로 디코딩한다. (torchcodec 우회)"""
    ffmpeg = shutil.which("ffmpeg")
    cmd = [ffmpeg, "-nostdin", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy(), sr


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

    # 파일 경로 대신 ffmpeg로 디코딩한 배열을 넘겨 torchcodec 문제를 피한다.
    audio, sr = decode_audio(audio_file_path)
    result = pipe({"raw": audio, "sampling_rate": sr})
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


# 화자 분리 함수
def speaker_diarization(
    audio_file_path: str,
    output_rttm_file_path: str,
    output_csv_file_path: str,
):
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HUGGINGFACE_API_KEY,
    )

    # CUDA를 사용할 수 있다면 CUDA를 사용하도록 설정
    if torch.cuda.is_available():
        diarization_pipeline.to(torch.device("cuda"))
        print("cuda is available")
    else:
        print("cuda is not available")

    # 파일 경로 대신 파형(waveform)을 넘겨 torchcodec 문제를 피한다.
    audio, sr = decode_audio(audio_file_path)
    waveform = torch.from_numpy(audio).unsqueeze(0)  # (channel=1, time)
    output = diarization_pipeline({"waveform": waveform, "sample_rate": sr})

    # 최신 pyannote는 DiarizeOutput을 반환 → .speaker_diarization 이 기존 Annotation 객체
    diarization = output.speaker_diarization

    with open(output_rttm_file_path, "w", encoding="utf-8") as rttm:
        diarization.write_rttm(rttm)

    df_rttm = pd.read_csv(
        output_rttm_file_path,
        sep=" ",
        header=None,
        names=["type", "file", "chnl", "start", "duration",
               "C1", "C2", "speaker_id", "C3", "C4"],
    )

    df_rttm["end"] = df_rttm["start"] + df_rttm["duration"]

    df_rttm["number"] = None
    df_rttm.at[0, "number"] = 0

    for i in range(1, len(df_rttm)):
        if df_rttm.at[i, "speaker_id"] != df_rttm.at[i - 1, "speaker_id"]:
            df_rttm.at[i, "number"] = df_rttm.at[i - 1, "number"] + 1
        else:
            df_rttm.at[i, "number"] = df_rttm.at[i - 1, "number"]

    df_rttm_grouped = df_rttm.groupby("number").agg(
        start=pd.NamedAgg(column="start", aggfunc="min"),
        end=pd.NamedAgg(column="end", aggfunc="max"),
        speaker_id=pd.NamedAgg(column="speaker_id", aggfunc="first"),
    )

    df_rttm_grouped["duration"] = df_rttm_grouped["end"] - df_rttm_grouped["start"]

    df_rttm_grouped.to_csv(
        output_csv_file_path,
        index=False,
        encoding="utf-8",
    )
    return df_rttm_grouped


if __name__ == "__main__":
    # 경로 끝에 쉼표(,)를 붙이면 튜플이 되어 버리므로 붙이지 않는다.
    audio_file_path = os.path.join(BASE_DIR, "audio", "싼기타_비싼기타.mp3")
    stt_output_file_path = os.path.join(BASE_DIR, "audio", "싼기타_비싼기타.csv")
    rttm_file_path = os.path.join(BASE_DIR, "audio", "싼기타_비싼기타.rttm")
    rttm_csv_file_path = os.path.join(BASE_DIR, "audio", "싼기타_비싼기타_rttm.csv")

    result, df = whisper_stt(
        audio_file_path,
        stt_output_file_path,
    )
    print(df)

    df_rttm = speaker_diarization(
        audio_file_path,
        rttm_file_path,
        rttm_csv_file_path,
    )
    print(df_rttm)
