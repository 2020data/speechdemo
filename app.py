import streamlit as st
import openai
import speech_recognition as sr

# ── 頁面設定 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎙️ 高效語音輸入模組",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ 高效語音輸入模組")
st.markdown("點擊麥克風開始錄音，完成後點擊停止，文字將自動填入下方欄位。")

# ── Session State 初始化 ───────────────────────────────────────────────────────
# 用來儲存辨識出來的文字，讓它可以顯示在輸入框中
if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""

# ── Sidebar 設定 ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 設定")
    language = st.selectbox(
        "辨識語言",
        ["zh-TW", "zh", "en", "ja", "ko"],
        index=0,
        help="zh-TW = 台灣中文，zh = 簡體中文"
    )
    api_key = st.text_input(
        "OpenAI API Key（選填）",
        type="password",
        placeholder="sk-...",
        help="輸入 Key 則使用 Whisper，留空則使用免費的 Google 語音辨識"
    )

# ── 語音辨識核心邏輯 ──────────────────────────────────────────────────────────
def transcribe_audio(audio_file, lang: str, api_key: str):
    """根據是否提供 API Key，決定使用 Whisper 或 Google 辨識"""
    
    # 1. 使用 OpenAI Whisper
    if api_key and api_key.startswith("sk-"):
        try:
            client = openai.OpenAI(api_key=api_key)
            # Streamlit 的 audio_file 已經是類似檔案的物件，補上檔名讓 Whisper 認得
            audio_file.name = "recording.wav" 
            
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=lang.split("-")[0], # Whisper 語言代碼通常用兩碼 (zh, en)
                response_format="text"
            )
            return result.strip()
        except Exception as e:
            return f"❌ Whisper 辨識錯誤: {e}"

    # 2. 使用 Google Web Speech API (免費)
    else:
        try:
            recognizer = sr.Recognizer()
            # 直接讀取 Streamlit 產生的 WAV 檔案
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=lang)
            return text
        except sr.UnknownValueError:
            return "⚠️ 無法辨識語音，請說得更清楚一點。"
        except sr.RequestError as e:
            return f"❌ Google API 連線錯誤：{e}"
        except Exception as e:
            return f"❌ 系統錯誤：{e}"

# ── 錄音與文字介面 ────────────────────────────────────────────────────────────

# 使用 Streamlit 官方原生的錄音元件 (Streamlit 1.38+ 支援)
audio_value = st.audio_input("請說話...")

# 當使用者錄音完畢並送出時
if audio_value is not None:
    with st.spinner("🔄 正在轉換為文字..."):
        # 進行辨識
        text_result = transcribe_audio(audio_value, language, api_key)
        # 將結果存入 session_state
        st.session_state.recognized_text = text_result
    
    # 清空 audio_value 避免畫面重複觸發（利用 rerun）
    st.rerun()

# ── 文字編輯區 ────────────────────────────────────────────────────────────────
st.markdown("### 📝 編輯與確認")

# 將 session_state 中的文字綁定到 text_area
edited_text = st.text_area(
    "辨識結果（可直接修改）",
    value=st.session_state.recognized_text,
    height=150
)

# 提供一個按鈕讓使用者可以做後續處理 (例如送出表單、儲存等)
if st.button("✅ 確認送出", use_container_width=True):
    if edited_text.strip():
        st.success("已成功送出！(你可以在這裡接上後續的處理邏輯)")
        # st.write("送出的內容：", edited_text)
    else:
        st.warning("請先錄音或輸入文字！")
