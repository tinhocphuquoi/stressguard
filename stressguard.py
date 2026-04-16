import streamlit as st
import google.generativeai as genai
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="AI StressGuard Student", page_icon="🧠", layout="wide")

st.title("🧠 AI StressGuard Student")
st.markdown("**Trợ lý sức khỏe tâm lý dành cho học sinh THCS & THPT**")

# Sidebar
with st.sidebar:
    st.header("🔑 Cài đặt")
    api_key = st.text_input("Gemini API Key", type="password", value="")
    model_name = st.selectbox("Chọn mô hình AI", 
                             ["gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite"], 
                             index=0)
    if api_key:
        genai.configure(api_key=api_key)
        st.success(f"✅ Đã kết nối {model_name}")
    
    st.markdown("---")
    st.markdown("**Tác giả:** Trần Quốc Thông  \n**Trường:** THCS và THPT Phú Quới")
    st.caption("Dự án thi HSG Tin học phần mềm sáng tạo 2026")

# Lưu dữ liệu
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

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Nhật ký cá nhân", 
    "📸 Phân tích ảnh mặt", 
    "📊 Thống kê cá nhân", 
    "📋 Báo cáo Lớp (Giáo viên)", 
    "💬 Chatbot AI 24/7"
])

# TAB 1: Nhật ký cá nhân
with tab1:
    st.subheader("Hôm nay bạn cảm thấy thế nào?")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.select_slider("Mức độ stress (0-10)", options=range(0, 11), value=5)
    with col2:
        emotion = st.selectbox("Cảm xúc chính", 
            ["😊 Vui vẻ", "😐 Bình thường", "😟 Lo lắng", "😢 Buồn", "😡 Tức giận", "😴 Mệt mỏi", "🤯 Quá tải"])
    note = st.text_area("Viết vài dòng về hôm nay (học tập, bạn bè, gia đình...)", height=150)
    
    if st.button("💾 Lưu nhật ký & Phân tích AI", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Vui lòng nhập Gemini API Key ở sidebar!")
        else:
            with st.spinner("AI đang phân tích..."):
                model = genai.GenerativeModel(model_name)
                prompt = f"""Bạn là chuyên gia tâm lý dành cho học sinh THCS và THPT Việt Nam. 
Phân tích mức stress {mood}/10, cảm xúc {emotion}, nhật ký: {note}. 
Đưa lời khuyên ngắn gọn, tích cực, dễ thực hiện bằng tiếng Việt, gần gũi với học sinh cấp 2 và cấp 3."""
                response = model.generate_content(prompt)
                ai_advice = response.text
                
                entry = {
                    "date": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M"),
                    "mood": mood, "emotion": emotion, "note": note, "ai_advice": ai_advice
                }
                st.session_state.data.append(entry)
                save_data(st.session_state.data)
                st.success("✅ Đã lưu nhật ký và phân tích thành công!")
                st.markdown("### 🤖 Phân tích từ AI:")
                st.write(ai_advice)
                st.rerun()

# TAB 2, 3, 4, 5 giữ nguyên như phiên bản trước (để code không quá dài)
# (Bạn có thể copy phần còn lại từ code cũ nếu cần, hoặc mình sẽ gửi bổ sung nếu bạn muốn)

st.caption("AI StressGuard Student • Tác giả: Trần Quốc Thông • Trường THCS & THPT Phú Quới • Gemini Flash-Lite • 2026")
