"""
本機錄音模組（PyAudio 版）
適合在本機執行、不透過瀏覽器錄音時使用。
執行方式：python recorder_local.py
"""
import pyaudio
import numpy as np
import wave
import io
import speech_recognition as sr


class SilenceDetectRecorder:
    """
    錄音直到偵測到連續 silence_sec 秒的靜音為止。
    """
    def __init__(
        self,
        silence_threshold: int = 500,   # RMS 低於此值視為靜音
        silence_sec: float = 1.0,       # 靜音幾秒後停止
        sample_rate: int = 16000,
        chunk: int = 1024,
        channels: int = 1,
    ):
        self.threshold = silence_threshold
        self.silence_sec = silence_sec
        self.rate = sample_rate
        self.chunk = chunk
        self.channels = channels
        self.fmt = pyaudio.paInt16

    def _rms(self, data: bytes) -> float:
        arr = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        return float(np.sqrt(np.mean(arr ** 2))) if len(arr) else 0.0

    def record(self) -> bytes:
        """開始錄音，回傳 WAV bytes"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.fmt,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        frames = []
        # 每 chunk 代表多少秒
        chunk_sec = self.chunk / self.rate
        # 需要連續幾個靜音 chunk 才停止
        silent_chunks_needed = int(self.silence_sec / chunk_sec)

        silent_count = 0
        has_speech = False
        print("🎙️  錄音開始，說完後停頓 1 秒自動結束...")

        try:
            while True:
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                rms = self._rms(data)

                if rms > self.threshold:
                    has_speech = True
                    silent_count = 0
                elif has_speech:
                    silent_count += 1
                    if silent_count >= silent_chunks_needed:
                        print("✅  偵測到靜音，錄音結束")
                        break
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

        # 封裝成 WAV
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.fmt))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(frames))
        return buf.getvalue()


def google_stt(audio_bytes: bytes, language: str = "zh-TW") -> str:
    recognizer = sr.Recognizer()
    audio_io = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_io) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "⚠️ 無法辨識"
    except sr.RequestError as e:
        return f"❌ 錯誤：{e}"


if __name__ == "__main__":
    recorder = SilenceDetectRecorder(silence_threshold=500, silence_sec=1.0)
    wav_bytes = recorder.record()

    # 儲存音檔
    with open("recording.wav", "wb") as f:
        f.write(wav_bytes)
    print("💾  已儲存 recording.wav")

    # 辨識
    print("🔄  辨識中...")
    text = google_stt(wav_bytes, language="zh-TW")
    print(f"📝  辨識結果：{text}")
