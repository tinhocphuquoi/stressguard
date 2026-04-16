import streamlit as st
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo   # ← Thêm dòng này để lấy giờ Việt Nam
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="AI StressGuard Student", page_icon="🧠", layout="wide")
st.title("🧠 AI StressGuard Student")
st.markdown("**Trợ lý sức khỏe tâm lý THPT** – Phân tích cảm xúc + Chatbot AI 24/7 (Giờ Việt Nam)")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🔑 Cài đặt")
    api_key = st.text_input("Gemini API Key", type="password", value="")
    model_name = st.selectbox("Chọn mô hình AI", 
                             ["gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite"], 
                             index=0)
    if api_key:
        genai.configure(api_key=api_key)
        st.success(f"✅ Đã kết nối {model_name}")

# ====================== LƯU DỮ LIỆU ======================
DATA_FILE = Path("stress_data.json")

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data_list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ====================== TABS ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Nhật ký cá nhân", 
    "📸 Phân tích ảnh mặt", 
    "📊 Thống kê cá nhân", 
    "📋 Báo cáo Lớp (Giáo viên)", 
    "💬 Chatbot AI 24/7"
])

# ==================== TAB 5: CHATBOT AI 24/7 (Giờ Việt Nam) ====================
with tab5:
    st.subheader("💬 Chatbot AI trò chuyện trực tiếp 24/7")
    st.caption("⏰ Đang hiển thị theo giờ Việt Nam (UTC+7)")
    
    chat_style = st.selectbox("Phong cách trò chuyện", ["Thân thiện ❤️", "Chuyên nghiệp 📋", "Cân bằng ⚖️"])
    
    # Khởi tạo lịch sử chat
    if "messages" not in st.session_state:
        vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
        st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình là AI StressGuard. Hôm nay bạn muốn chia sẻ gì? ❤️", "timestamp": vn_time}]

    # Hiển thị tin nhắn kèm giờ Việt Nam
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"**{msg.get('timestamp', '')}** — {msg['content']}")

    # Nhập tin nhắn
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
        
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": vn_time})
        with st.chat_message("user"):
            st.markdown(f"**{vn_time}** — {prompt}")

        with st.chat_message("assistant"):
            with st.spinner("AI đang suy nghĩ..."):
                model = genai.GenerativeModel(model_name)
                style_prompt = {
                    "Thân thiện ❤️": "Bạn là người bạn rất thân thiện, ấm áp, hay dùng emoji.",
                    "Chuyên nghiệp 📋": "Bạn là chuyên gia tâm lý chuyên nghiệp, trả lời logic và rõ ràng.",
                    "Cân bằng ⚖️": "Bạn vừa thân thiện vừa chuyên nghiệp."
                }[chat_style]
                
                full_prompt = style_prompt + "\n\nLịch sử:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                response = model.generate_content(full_prompt)
                ai_reply = response.text
                
                st.markdown(f"**{vn_time}** — {ai_reply}")
                st.session_state.messages.append({"role": "assistant", "content": ai_reply, "timestamp": vn_time})

    # Nút chức năng
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")
            st.session_state.messages = [{"role": "assistant", "content": "Đã xóa lịch sử. Chúng ta bắt đầu lại nhé!", "timestamp": vn_time}]
            st.rerun()
    with col2:
        if st.button("💾 Lưu cuộc trò chuyện vào nhật ký", use_container_width=True):
            if len(st.session_state.messages) > 1:
                chat_text = "\n".join([f"{m['timestamp']} {m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
                entry = {"date": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M"), 
                        "mood": 5, "emotion": "Từ chatbot", "note": chat_text, "ai_advice": "Đã lưu từ chatbot"}
                st.session_state.data.append(entry)
                save_data(st.session_state.data)
                st.success("✅ Đã lưu cuộc trò chuyện vào nhật ký!")

# (Các tab 1,2,3,4 giữ nguyên như code trước để tránh lỗi)
# Tab 1,2,3,4 được giữ nguyên đầy đủ trong code thực tế, mình chỉ rút gọn để tin nhắn không quá dài.

st.caption("AI StressGuard Student • Gemini Flash-Lite • Giờ Việt Nam (UTC+7) • Thi HSG 2026")
