import streamlit as st
import base64
import io
import wave
import numpy as np
import openai
import tempfile
import os
from streamlit_realtime_audio_recorder import audio_recorder

# ── 頁面設定 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎙️ 語音辨識模組",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ 語音辨識模組")
st.markdown(
    "說完話後，停頓 **1 秒** 即自動停止錄音並轉換為文字。",
    unsafe_allow_html=False
)

# ── Sidebar 設定 ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 設定")
    silence_timeout = st.slider(
        "停頓偵測時間（毫秒）", 500, 3000, 1000, step=100,
        help="說完話後靜音多久自動停止"
    )
    silence_threshold = st.slider(
        "靜音閾值（dB）", -80, -30, -60, step=5,
        help="低於此音量視為靜音，數值越小越靈敏"
    )
    language = st.selectbox(
        "辨識語言",
        ["zh", "zh-TW", "en", "ja", "ko"],
        index=0,
        help="zh = 普通話，zh-TW = 台灣中文"
    )
    api_key = st.text_input(
        "OpenAI API Key（Whisper）",
        type="password",
        placeholder="sk-...",
        help="使用 Whisper API 辨識，留空則使用 Google"
    )

# ── Session State 初始化 ───────────────────────────────────────────────────────
if "transcripts" not in st.session_state:
    st.session_state.transcripts = []
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

# ── 語音辨識函式 ──────────────────────────────────────────────────────────────
def transcribe_with_whisper(audio_bytes: bytes, lang: str, key: str) -> str:
    """使用 OpenAI Whisper API 辨識"""
    client = openai.OpenAI(api_key=key)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=lang.split("-")[0],  # whisper 只用 ISO 639-1
                response_format="text"
            )
        return result.strip()
    finally:
        os.unlink(tmp_path)

def transcribe_with_google(audio_bytes: bytes, lang: str) -> str:
    """使用 Google Web Speech API（免費，需網路）"""
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    audio_io = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_io) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language=lang)
        return text
    except sr.UnknownValueError:
        return "⚠️ 無法辨識語音，請再試一次"
    except sr.RequestError as e:
        return f"❌ Google API 錯誤：{e}"

def transcribe(audio_bytes: bytes, lang: str, api_key: str) -> str:
    if api_key and api_key.startswith("sk-"):
        return transcribe_with_whisper(audio_bytes, lang, api_key)
    return transcribe_with_google(audio_bytes, lang)

def base64_to_wav_bytes(b64_data: str) -> bytes:
    """將 base64 WebM/WAV 轉成 WAV bytes"""
    raw = base64.b64decode(b64_data)
    return raw  # streamlit-realtime-audio-recorder 已回傳 WAV

# ── 錄音元件 ──────────────────────────────────────────────────────────────────
# ── 錄音元件 ──────────────────────────────────────────────────────────────────
st.markdown("### 🔴 點擊麥克風開始錄音")

# 1. 移除 key="recorder" 參數
result = audio_recorder(
    interval=50,                        # 每 50ms 檢查一次音量
    threshold=silence_threshold,        # 靜音閾值 dB
    silenceTimeout=silence_timeout,     # 停頓多少 ms 後停止
    play=False
)

# ── 處理錄音結果 ──────────────────────────────────────────────────────────────
# 2. 解析回傳的字典，提取出實際的音訊字串 (audioData)
if result and isinstance(result, dict) and result.get('status') == 'stopped':
    audio_b64 = result.get('audioData')
    
    # 確保有音訊且沒有重複處理
    if audio_b64 and audio_b64 != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_b64  # 記錄當前音檔，防止重複處理

        audio_bytes = base64_to_wav_bytes(audio_b64)
        st.audio(audio_bytes, format="audio/wav")

        with st.spinner("🔄 辨識中..."):
            text = transcribe(audio_bytes, language, api_key)

        st.success(f"📝 辨識結果：**{text}**")
        st.session_state.transcripts.append(text)


# ── 歷史記錄 ─────────────────────────────────────────────────────────────────
if st.session_state.transcripts:
    st.markdown("---")
    st.markdown("### 📋 辨識記錄")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 清除全部"):
            st.session_state.transcripts = []
            st.rerun()

    for i, t in enumerate(reversed(st.session_state.transcripts), 1):
        st.write(f"**{i}.** {t}")

    full_text = "\n".join(st.session_state.transcripts)

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            "⬇️ 下載 TXT",
            full_text,
            file_name="transcript.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_b:
        st.text_area("全文預覽", full_text, height=120)
