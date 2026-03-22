import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io

# 設定頁面配置
st.set_page_config(page_title="進階語音辨識系統", page_icon="🎙️", layout="centered")

# === 頂級感 CSS 樣式設定 ===
st.markdown("""
    <style>
    /* 整體背景與字體 */
    .main { background-color: #0E1117; }
    .stTextArea textarea {
        background-color: #1A1C24;
        color: #E0E0E0;
        border: 1px solid #3E424B;
        border-radius: 10px;
        font-size: 16px;
    }
    /* 標題樣式 */
    .app-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #FFFFFF;
        text-align: center;
        padding: 20px;
        font-weight: 300;
        letter-spacing: 2px;
    }
    /* 分隔線 */
    hr { border-top: 1px solid #3E424B; }
    </style>
    <div class="app-header"><h1>VOICE INTELLIGENCE</h1></div>
    """, unsafe_allow_html=True)

# === 1. 初始化 Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

# === 2. 歷史對話視窗 (上半部) ===
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

st.markdown("---")

# === 3. 錄音核心區 (中央) ===
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # 錄音按鈕配置
    audio_bytes = audio_recorder(
        text="",
        recording_color="#FF3B30",  # 高級感緋紅
        neutral_color="#10B981",    # 祖母綠
        icon_name="microphone",
        icon_size="4x",
        pause_threshold=1.0         # 1秒靜音自動停止
    )

# === 4. 語音辨識邏輯 ===
if audio_bytes and audio_bytes != st.session_state.last_audio:
    st.session_state.last_audio = audio_bytes
    
    with st.spinner("系統分析中..."):
        audio_file = io.BytesIO(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        
        try:
            # 進行 Google 語音辨識 (繁體中文)
            recognized_text = r.recognize_google(audio_data, language="zh-TW")
            
            # 更新當前編輯框的文字
            st.session_state.current_text = recognized_text
            
            # 同步將結果存入對話歷史
            st.session_state.messages.append({"role": "user", "content": recognized_text})
            
        except sr.UnknownValueError:
            st.toast("未能辨識清晰語音", icon="❌")
        except sr.RequestError:
            st.error("網路辨識服務暫時無法連線")

# === 5. 編輯框與功能按鈕 (下半部) ===
# 辨識結果文字框
edited_text = st.text_area(
    "辨識結果與編輯區", 
    value=st.session_state.current_text, 
    height=150, 
    placeholder="語音辨識後文字將出現在此，您也可以直接編輯..."
)

# 輔助功能按鈕
c1, c2 = st.columns([1, 1])
with c1:
    if st.button("清除對話紀錄", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_text = ""
        st.rerun()
with c2:
    if st.button("複製當前文字", use_container_width=True):
        st.toast("文字已更新並儲存於對話紀錄中", icon="✅")

# 頁尾說明
st.caption("Designed for Professional Transcription | 停頓一秒自動結束")
