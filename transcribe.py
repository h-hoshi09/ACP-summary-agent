# transcribe.py
import whisper
import sys
import soundfile as sf
import io

def transcribe(audio_path, output_path="transcript.txt"):
    model = whisper.load_model("medium")
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_np, _ = sf.read(io.BytesIO(audio_bytes))
    result = model.transcribe(audio_np.astype("float32"))
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(result["text"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("音声ファイルのパスを指定してください。")
    else:
        transcribe(sys.argv[1])