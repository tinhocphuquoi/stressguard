import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from PIL import Image
import io

# ====================== CẤU HÌNH ======================
st.set_page_config(page_title="AI StressGuard Student", page_icon="🧠", layout="wide")
st.title("🧠 AI StressGuard Student")
st.markdown("**Trợ lý sức khỏe tâm lý học sinh** – Phân tích cảm xúc với AI")

# Sidebar
with st.sidebar:
    st.header("🔑 Cài đặt")
    api_key = st.text_input("Gemini API Key", type="password", value="", help="Lấy miễn phí tại aistudio.google.com")
    
    model_name = st.selectbox(
        "Chọn mô hình AI",
        options=["gemini-3.1-flash-lite-preview", "gemini-2.5-flash-lite"],
        index=0
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success(f"✅ Đã kết nối {model_name}")
    
    st.info("💡 Dữ liệu lưu cục bộ trên máy bạn")

# ====================== LƯU DỮ LIỆU ======================
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

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📝 Nhật ký cá nhân", "📸 Phân tích ảnh mặt", "📊 Thống kê cá nhân", "📋 Báo cáo Lớp (Giáo viên)"])

# ==================== TAB 1: Nhật ký cá nhân ====================
with tab1:
    st.subheader("Hôm nay bạn cảm thấy thế nào?")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.select_slider("Mức độ stress (0 = rất vui → 10 = cực kỳ stress)", options=range(0, 11), value=5)
    with col2:
        emotion = st.selectbox("Cảm xúc chính", 
            ["😊 Vui vẻ", "😐 Bình thường", "😟 Lo lắng", "😢 Buồn", "😡 Tức giận", "😴 Mệt mỏi", "🤯 Quá tải"])

    note = st.text_area("Viết vài dòng về hôm nay...", height=120)

    if st.button("💾 Lưu nhật ký & Phân tích AI", type="primary"):
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key!")
        else:
            model = genai.GenerativeModel(model_name)
            prompt = f"""Bạn là chuyên gia tâm lý học cho học sinh THPT Việt Nam.
Phân tích mức stress và đưa ra lời khuyên ngắn gọn, tích cực.
Dữ liệu: Stress {mood}/10, Cảm xúc: {emotion}, Nhật ký: {note}
Trả lời bằng tiếng Việt, tối đa 4-5 câu. Bắt đầu bằng "AI StressGuard nhận xét:"."""
            response = model.generate_content(prompt)
            ai_advice = response.text

            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "mood": mood,
                "emotion": emotion,
                "note": note,
                "ai_advice": ai_advice,
                "model": model_name
            }
            data.append(entry)
            save_data(data)
            st.success("✅ Đã lưu!")
            st.write(ai_advice)

# ==================== TAB 2: Phân tích ảnh mặt ====================
with tab2:
    st.subheader("📸 Upload ảnh khuôn mặt để AI đoán cảm xúc")
    uploaded_file = st.file_uploader("Chọn ảnh selfie (chỉ ảnh khuôn mặt rõ nét)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh bạn vừa upload", use_column_width=True)

        if st.button("🔍 Phân tích cảm xúc bằng AI Flash-Lite"):
            if not api_key:
                st.error("Vui lòng nhập API Key!")
            else:
                model = genai.GenerativeModel(model_name)
                prompt = """Phân tích cảm xúc khuôn mặt của học sinh THPT. 
Chỉ trả về cảm xúc chính (ví dụ: Vui vẻ, Buồn, Stress cao, Lo lắng, Mệt mỏi, Tức giận, Bình thường).
Sau đó đưa ra 1-2 câu khuyên ngắn gọn bằng tiếng Việt."""
                
                response = model.generate_content([prompt, image])
                result = response.text
                
                st.markdown("### 🤖 Kết quả phân tích cảm xúc")
                st.write(result)

                # Lưu luôn vào dữ liệu (tùy chọn)
                if st.checkbox("Lưu kết quả này vào nhật ký cá nhân"):
                    entry = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "mood": 5,
                        "emotion": "Từ ảnh mặt",
                        "note": "Phân tích từ ảnh",
                        "ai_advice": result,
                        "model": model_name
                    }
                    data.append(entry)
                    save_data(data)
                    st.success("Đã lưu vào nhật ký!")

# ==================== TAB 3: Thống kê cá nhân ====================
with tab3:
    if data:
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        st.plotly_chart(px.line(df, x='date', y='mood', markers=True, title="Mức stress theo thời gian"), use_container_width=True)
        st.dataframe(df[['date', 'mood', 'emotion', 'note']], use_container_width=True)
    else:
        st.info("Chưa có dữ liệu. Hãy ghi nhật ký trước.")

# ==================== TAB 4: Báo cáo Lớp cho Giáo viên ====================
with tab4:
    st.subheader("📋 Báo cáo lớp học (Giáo viên)")
    password = st.text_input("Nhập mật khẩu giáo viên", type="password")
    
    if password == "giao_vien_2026":
        st.success("✅ Xác thực thành công – Chế độ Giáo viên")
        if data:
            df = pd.DataFrame(data)
            avg_stress = df['mood'].mean()
            most_common_emotion = df['emotion'].mode()[0] if not df['emotion'].empty else "Chưa có"
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Học sinh đã ghi", len(df))
            col2.metric("Stress trung bình lớp", f"{avg_stress:.1f}/10")
            col3.metric("Cảm xúc phổ biến nhất", most_common_emotion)
            
            st.plotly_chart(px.histogram(df, x='mood', nbins=11, title="Phân bố mức stress của lớp"), use_container_width=True)
            st.plotly_chart(px.pie(df, names='emotion', title="Tỉ lệ cảm xúc"), use_container_width=True)
            
            st.dataframe(df[['date', 'mood', 'emotion']], use_container_width=True)
        else:
            st.info("Chưa có dữ liệu lớp nào.")
    else:
        if password:
            st.error("Mật khẩu sai! (Mật khẩu mặc định: giao_vien_2026)")

st.caption("AI StressGuard Student • Trần Quốc Thông - Trường THCS và THPT Phú Quới")