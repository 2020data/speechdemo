import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import io
import time

# 初始化 session state，用於儲存聊天消息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化錄音狀態
if "recording_started" not in st.session_state:
    st.session_state.recording_started = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# 應用程式標題和設定
st.set_page_config(page_title="🎤 對話語音辨識", page_icon="🗣️")
st.title("🎤 對話語音辨識應用")

# 顯示聊天記錄
# 遍歷 messages 列表並渲染每條消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 錄音控制區域
st.markdown("---")
st.subheader("開始新的對話")

# 用戶提示和說明
st.write("點擊下方麥克風圖示開始說話。停頓 1 秒將自動結束錄音。")
st.caption("提示：錄音計時器為模擬值。準確時間將在錄音完成後計算。")

# 建立實時計時器容器
# 在 st.empty() 中更新內容可以模擬實時流
timer_placeholder = st.empty()

# 如果正在錄音，更新計時器
if st.session_state.recording_started and st.session_state.start_time:
    elapsed_seconds = time.time() - st.session_state.start_time
    # 我們只在 Python rerun 時更新，這不是真正的實時流，而是一個方便的模擬。
    # 用戶必須點擊錄音按鈕才能重新運行 Python 並更新計時器。
    # 這個應用程式採用了這種方法，因為 audio_recorder() 函數是阻塞式的。
    # “顯示錄音秒數”這一個要求在無伺服器部署環境中，實時流（例如使用 Web Audio API）通常需要自定義 JavaScript 元件。
    # 我們選擇這種模擬方法，以保持代碼簡潔並易於部署。
    # 在部署環境中，這將是一個完成後的估計值，而不是真正的實時流。
    timer_placeholder.write(f"錄音時間: {elapsed_seconds:.1f} 秒")
else:
    timer_placeholder.empty()

# 使用 audio-recorder-streamlit，並將 pause_threshold 設置為 1 秒
# 這將處理麥克風權限和錄音
# 關鍵：1 秒靜音後自動停止
audio_bytes = audio_recorder(
    text="", 
    recording_color="#e8b62c", 
    neutral_color="#6aa36f", 
    icon_name="microphone", 
    icon_size="3x",
    pause_threshold=1.0,
)

# 處理錄音數據
# 當 `audio_bytes` 可用時，表示錄音已自動或手動完成
if audio_bytes:
    # 更新錄音狀態
    st.session_state.recording_started = False
    st.session_state.start_time = None
    timer_placeholder.empty() # 清空計時器容器
    
    # 顯示處理中狀態
    processing_placeholder = st.empty()
    processing_placeholder.info("處理中，請稍候...")

    # 計算準確的總錄音秒數 (粗略估計，假設 16000Hz Sample Rate, 16-bit Mono = 32000 bytes/sec)
    duration_seconds = len(audio_bytes) / 32000.0

    audio_file = io.BytesIO(audio_bytes)
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
    
    try:
        # 呼叫 Google 語音辨識 API
        # 設定為繁體中文
        text = r.recognize_google(audio_data, language="zh-TW")
        
        # 清空處理中狀態
        processing_placeholder.empty()

        # 將辨識出的文字和錄音時間添加到聊天記錄中
        # 這確保它「顯示在對話視窗」中
        message_content = f"辨識結果：{text} (約 {duration_seconds:.1f} 秒)"
        st.session_state.messages.append({"role": "user", "content": message_content})
        
        # 進一步回應 (可選)
        # 您可以添加機器人回應，例如：
        # st.session_state.messages.append({"role": "assistant", "content": f"您剛剛說了: '{text}'，共 {duration_seconds:.1f} 秒。"})

        # 觸發 rerun 以刷新聊天視窗並顯示新消息
        st.rerun()
        
    except sr.UnknownValueError:
        # 無法辨識
        processing_placeholder.empty()
        st.warning("無法辨識，請再試一次。")
    except sr.RequestError as e:
        # API 請求錯誤
        processing_placeholder.empty()
        st.error(f"API 請求錯誤：{e}")

