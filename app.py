import streamlit as st
import speech_recognition as sr

def recognize_speech_from_mic():
    # 初始化語音辨識器
    r = sr.Recognizer()
    
    # 【關鍵設定】設定停頓 1 秒即當作一句話結束，自動終止錄音
    r.pause_threshold = 1.0  

    # 使用預設麥克風作為音訊來源
    with sr.Microphone() as source:
        st.info("🎙️ 請開始說話... (停頓 1 秒將自動停止錄音)")
        
        # 自動適應環境噪音（花費 0.5 秒取樣背景噪音）
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # listen 函式會阻塞直到收到聲音，並在停頓超過 pause_threshold 後自動結束
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            st.success("✅ 錄音結束，正在辨識中...")
            
            # 使用 Google Web Speech API 進行辨識 (語言設定為繁體中文)
            text = r.recognize_google(audio, language="zh-TW")
            return text, None
            
        except sr.WaitTimeoutError:
            return None, "超過時間未偵測到聲音，請再試一次。"
        except sr.UnknownValueError:
            return None, "無法辨識您說的內容，可能是環境雜音過大或聲音太小。"
        except sr.RequestError as e:
            return None, f"無法連線至 Google 語音辨識服務：{e}"
        except Exception as e:
            return None, f"發生未知的錯誤：{e}"

# --- Streamlit 介面 ---
st.title("語音辨識與文字轉換模組")
st.markdown("點擊下方按鈕開始說話，系統會在**偵測到您停頓 1 秒後自動結束錄音**，並將文字顯示在畫面上。")

# 使用 session_state 來保留辨識紀錄
if "transcripts" not in st.session_state:
    st.session_state.transcripts = []

if st.button("開始錄音", type="primary"):
    with st.spinner("準備麥克風中..."):
        text, error = recognize_speech_from_mic()
        
    if text:
        st.session_state.transcripts.append(text)
    elif error:
        st.error(error)

# 顯示辨識結果
if st.session_state.transcripts:
    st.write("### 辨識結果：")
    for i, t in enumerate(reversed(st.session_state.transcripts)):
        st.info(f"對話 {len(st.session_state.transcripts) - i}: {t}")

