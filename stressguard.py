import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="AI StressGuard Student", page_icon="🧠", layout="wide")
st.title("🧠 AI StressGuard Student")
st.markdown("**Trợ lý sức khỏe tâm lý THPT** – Chatbot AI 24/7 + Phân tích cảm xúc")

# Sidebar
with st.sidebar:
    st.header("🔑 Cài đặt")
    api_key = st.text_input("Gemini API Key", type="password", value="")
    model_name = st.selectbox("Chọn mô hình AI", ["gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite"], index=0)
    if api_key:
        genai.configure(api_key=api_key)
        st.success(f"✅ Đã kết nối {model_name}")

# Lưu dữ liệu nhật ký
DATA_FILE = Path("stress_data.json")
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Nhật ký cá nhân", 
    "📸 Phân tích ảnh mặt", 
    "📊 Thống kê cá nhân", 
    "📋 Báo cáo Lớp", 
    "💬 Chatbot AI 24/7"
])

# ====================== TAB 5: CHATBOT AI 24/7 ======================
with tab5:
    st.subheader("💬 Chatbot AI trò chuyện trực tiếp 24/7")
    st.caption("AI StressGuard luôn sẵn sàng lắng nghe và hỗ trợ bạn")

    # Chọn phong cách chatbot
    chat_style = st.selectbox(
        "Chọn phong cách trò chuyện",
        options=["Thân thiện ❤️", "Chuyên nghiệp 📋", "Cân bằng ⚖️"],
        index=0
    )

    # Khởi tạo lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chào bạn! Mình là AI StressGuard. Hôm nay bạn muốn chia sẻ gì với mình nhỉ? ❤️"
        }]

    # Hiển thị lịch sử chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input tin nhắn
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI đang suy nghĩ..."):
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    # Tinh chỉnh prompt theo phong cách
                    if chat_style == "Thân thiện ❤️":
                        system_prompt = "Bạn là AI StressGuard, một người bạn rất thân thiện, ấm áp, hay dùng emoji, nói chuyện như bạn bè với học sinh THPT."
                    elif chat_style == "Chuyên nghiệp 📋":
                        system_prompt = "Bạn là AI StressGuard, một chuyên gia tư vấn tâm lý chuyên nghiệp, trả lời trang trọng, logic và có cấu trúc rõ ràng."
                    else:
                        system_prompt = "Bạn là AI StressGuard, vừa thân thiện vừa chuyên nghiệp, cân bằng giữa sự gần gũi và lời khuyên có giá trị."
                    
                    full_prompt = system_prompt + "\n\nLịch sử trò chuyện:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    response = model.generate_content(full_prompt)
                    ai_reply = response.text
                except:
                    ai_reply = "Xin lỗi, mình đang bận một chút. Bạn thử lại sau nhé!"

                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # Nút chức năng
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Lịch sử chat đã được xóa. Chúng ta bắt đầu lại nhé! ❤️"
            }]
            st.rerun()

    with col2:
        if st.button("💾 Lưu cuộc trò chuyện vào nhật ký", use_container_width=True):
            if len(st.session_state.messages) > 1:
                chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
                entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "mood": 5,
                    "emotion": "Từ chatbot",
                    "note": f"Cuộc trò chuyện AI:\n{chat_history}",
                    "ai_advice": "Đã lưu từ chatbot",
                    "model": model_name
                }
                data.append(entry)
                save_data(data)
                st.success("✅ Đã lưu toàn bộ cuộc trò chuyện vào nhật ký cá nhân!")
            else:
                st.warning("Chưa có cuộc trò chuyện nào để lưu.")

st.caption("AI StressGuard Student • Gemini Flash-Lite • Chatbot 24/7 • Dành cho thi HSG Tin học 2026")
