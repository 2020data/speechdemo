import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io

# 設定頁面標題與版面
st.set_page_config(page_title="語音辨識對話系統", page_icon="🎤", layout="centered")

# 自定義 CSS 讓 UI 更美觀（可選）
st.markdown("""
    <style>
    .stChatFloatingInputContainer { background-color: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

# === 1. 初始化 Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# === 2. 顯示對話歷史紀錄 (對話視窗) ===
st.title("🗣️ 語音對話助手")
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# === 3. 錄音控制區 ===
st.write("") # 增加間距
st.write("") 

# 使用固定底部的容器或置中顯示
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("      點擊麥克風開始說話")
    # 錄音元件：放大圖示並設定顏色
    # pause_threshold=1.0：停頓 1 秒自動中止
    audio_bytes = audio_recorder(
        text="",
        recording_color="#FF4B4B", # 錄音中：紅色
        neutral_color="#28a745",   # 平常/停止：綠色
        icon_name="microphone",
        icon_size="4x",            # 放大圖案
        pause_threshold=1.0
    )

# === 4. 語音辨識與對話框輸出 ===
if audio_bytes and audio_bytes != st.session_state.last_audio:
    st.session_state.last_audio = audio_bytes
    
    with st.spinner("正在辨識語音..."):
        audio_file = io.BytesIO(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        
        try:
            # 辨識繁體中文
            text = r.recognize_google(audio_data, language="zh-TW")
            
            # 將辨識文字存入對話紀錄
            st.session_state.messages.append({"role": "user", "content": text})
            
            # 重新整理頁面以顯示最新的對話框
            st.rerun()
            
        except sr.UnknownValueError:
            st.toast("⚠️ 抱歉，我沒聽清楚，請再試一次。", icon="🎙️")
        except sr.RequestError:
            st.error("連線錯誤，請檢查網路。")

# 頁尾提示
st.markdown("---")
st.caption("💡 提示：說完話後請靜止 1 秒，系統會自動辨識並將文字傳送到對話視窗。")
