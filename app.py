import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

st.set_page_config(page_title="語音轉文字助理", page_icon="🎙️")

st.title("🎙️ 語音輸入模組")
st.write("點擊下方按鈕開始說話，停止錄音後系統將自動顯示文字。")

# 建立辨識器
recognizer = sr.Recognizer()

# 介面佈局
col1, col2 = st.columns([1, 3])

with col1:
    # 錄音組件
    audio = mic_recorder(
        start_prompt="開始錄音 🎤",
        stop_prompt="停止錄音 ⏹️",
        key='recorder'
    )

if audio:
    # 讀取錄製的音訊內容
    audio_bio = io.BytesIO(audio['bytes'])
    
    with st.spinner("正在辨識語音中..."):
        try:
            with sr.AudioFile(audio_bio) as source:
                audio_data = recognizer.record(source)
                # 使用 Google 辨識 (zh-TW)
                text = recognizer.recognize_google(audio_data, language="zh-TW")
                
                st.success("辨識成功！")
                st.text_area("辨識結果：", value=text, height=150)
                
                # 提供下載或複製功能
                st.download_button("下載文字檔", text, file_name="speech_to_text.txt")
                
        except sr.UnknownValueError:
            st.warning("抱歉，無法辨識語音內容，請再試一次。")
        except Exception as e:
            st.error(f"發生錯誤: {e}")

# 側邊欄說明
with st.sidebar:
    st.header("使用說明")
    st.info("1. 點擊按鈕開始錄音。\n2. 說完話後點擊停止（或靜音自動停止）。\n3. 系統會自動將語音轉為繁體中文。")
