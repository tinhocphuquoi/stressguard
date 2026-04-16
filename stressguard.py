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
st.markdown("**Trợ lý sức khỏe tâm lý THPT** – Phân tích cảm xúc + Chatbot AI 24/7")

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

# Sử dụng session_state để dữ liệu được đồng bộ toàn app
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

# ==================== TAB 1: Nhật ký cá nhân ====================
with tab1:
    st.subheader("Hôm nay bạn cảm thấy thế nào?")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.select_slider("Mức độ stress (0-10)", options=range(0, 11), value=5)
    with col2:
        emotion = st.selectbox("Cảm xúc chính", 
            ["😊 Vui vẻ", "😐 Bình thường", "😟 Lo lắng", "😢 Buồn", "😡 Tức giận", "😴 Mệt mỏi", "🤯 Quá tải"])
    note = st.text_area("Viết vài dòng về hôm nay...", height=120)
    
    if st.button("💾 Lưu nhật ký & Phân tích AI", type="primary"):
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key!")
        else:
            model = genai.GenerativeModel(model_name)
            prompt = f"""Bạn là chuyên gia tâm lý cho học sinh THPT Việt Nam. Phân tích mức stress {mood}/10, cảm xúc {emotion}, nhật ký: {note}. Đưa lời khuyên ngắn gọn, tích cực bằng tiếng Việt."""
            response = model.generate_content(prompt)
            ai_advice = response.text
            
            entry = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "mood": mood, "emotion": emotion, "note": note, "ai_advice": ai_advice}
            st.session_state.data.append(entry)
            save_data(st.session_state.data)
            st.success("✅ Đã lưu!")
            st.write(ai_advice)
            st.rerun()

# ==================== TAB 3: Thống kê cá nhân (ĐÃ SỬA) ====================
with tab3:
    st.subheader("📊 Thống kê cá nhân")
    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        df['date'] = pd.to_datetime(df['date'])
        st.plotly_chart(px.line(df, x='date', y='mood', markers=True, title="Mức stress theo thời gian"), use_container_width=True)
        st.dataframe(df[['date', 'mood', 'emotion', 'note']], use_container_width=True)
        
        # NÚT XÓA ĐÃ ĐƯỢC SỬA
        st.markdown("---")
        if st.button("🗑️ Xóa toàn bộ nhật ký cá nhân", type="secondary"):
            if st.checkbox("Tôi chắc chắn muốn xóa HẾT dữ liệu (không thể khôi phục lại)"):
                st.session_state.data = []
                save_data([])
                if DATA_FILE.exists():
                    DATA_FILE.unlink()   # Xóa file vật lý
                st.success("✅ Đã xóa toàn bộ nhật ký cá nhân!")
                st.rerun()
    else:
        st.info("Chưa có dữ liệu nhật ký nào.")

# (Các tab còn lại giữ nguyên như code trước, mình rút gọn để code ngắn hơn)

st.caption("AI StressGuard Student • Gemini Flash-Lite • Dành cho thi HSG Tin học 2026")
