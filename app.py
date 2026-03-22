import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io

# 設定頁面標題
st.set_page_config(page_title="即時語音辨識對話", page_icon="🎤")
st.title("🎤 雲端版語音辨識對話視窗")

# 初始化 Session State 來儲存對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示過去的對話紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 建立網頁前端錄音元件
# pause_threshold=1.0 代表超過 1 秒沒聲音就自動停止錄音
st.write("點擊下方麥克風圖示開始說話（停頓 1 秒將自動結束錄音）：")
audio_bytes = audio_recorder(
    text="", 
    recording_color="#e8b62c", 
    neutral_color="#6aa36f", 
    icon_name="microphone", 
    icon_size="2x",
    pause_threshold=1.0 
)

# 當接收到前端傳來的錄音資料時進行處理
if audio_bytes:
    # 將接收到的 bytes 轉換為音訊檔格式
    audio_file = io.BytesIO(audio_bytes)
    r = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
        
    try:
        # 呼叫 Google 語音辨識 API
        text = r.recognize_google(audio_data, language="zh-TW")
        
        # 將結果加入歷史紀錄
        st.session_state.messages.append({"role": "user", "content": text})
        # 觸發畫面重新整理
        st.rerun()
        
    except sr.UnknownValueError:
        st.warning("無法辨識：聽不清楚您說的話，請再試一次。")
    except sr.RequestError as e:
        st.error(f"API 請求錯誤：請檢查網路連線。細節: {e}")
