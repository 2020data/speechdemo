import streamlit as st
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="語音辨識模組", page_icon="🎤")

st.title("🎤 語音自動辨識模組")
st.write("點擊下方按鈕開始說話。瀏覽器會在偵測到您停止說話（約1秒）後，自動將語音轉為文字。")

st.markdown("---")

# 呼叫前端語音轉文字功能
text = speech_to_text(
    language='zh-TW',              # 設定為繁體中文
    start_prompt="點我開始說話 🔴", # 開始按鈕的文字
    stop_prompt="聆聽中... ⏹️",    # 錄音時按鈕的文字
    just_once=False,               # 允許重複使用
    key='STT'                      # 元件專屬 ID
)

# 當有辨識結果時顯示出來
if text:
    st.success("辨識完成！")
    st.text_area("您的語音內容：", value=text, height=150)
