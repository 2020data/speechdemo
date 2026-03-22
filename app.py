import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io

# 設定頁面標題
st.set_page_config(page_title="即時語音辨識對話", page_icon="🎤")

# === 初始化 Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# 【關鍵修正】新增一個狀態來記錄「最後一次處理過的音訊」
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# === 1. 顯示對話視窗 (上半部) ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === 2. 錄音控制區 (下半部) ===
st.markdown("---")
st.write("點擊下方麥克風圖示開始說話（停頓 1 秒將自動結束錄音）：")

# 錄音元件 (1秒靜音自動中斷)
audio_bytes = audio_recorder(
    text="", 
    recording_color="#e8b62c", 
    neutral_color="#6aa36f", 
    icon_name="microphone", 
    icon_size="2x",
    pause_threshold=1.0 
)

# === 3. 語音辨識與防重複處理機制 ===
# 條件判斷：必須有錄到音訊，且這段音訊「不等於」上次處理過的音訊
if audio_bytes and audio_bytes != st.session_state.last_audio:
    
    # 標記這段新音訊為「已處理」
    st.session_state.last_audio = audio_bytes
    
    # 使用 st.spinner 顯示短暫的處理動畫，處理完就會自動消失，不會殘留文字
    with st.spinner("辨識中..."):
        audio_file = io.BytesIO(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        
        try:
            # 呼叫 API 進行辨識
            text = r.recognize_google(audio_data, language="zh-TW")
            
            # 【關鍵要求】只將結果加到對話紀錄中，不在其他地方顯示
            st.session_state.messages.append({"role": "user", "content": text})
            
            # 觸發畫面重新整理，讓對話窗顯示最新訊息
            st.rerun()
            
        except sr.UnknownValueError:
            st.error("聽不清楚您說的話，請再試一次。")
        except sr.RequestError as e:
            st.error(f"API 請求錯誤：{e}")
