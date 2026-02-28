# app.py - موقع الكيان صفر
import streamlit as st
import time

# إعدادات الصفحة
st.set_page_config(
    page_title="الكيان صفر | Entity Zero",
    page_icon="🕵️",
    layout="centered"
)

# CSS مخصص
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
        color: #00ff00;
    }
    .stButton > button {
        background-color: #0d47a1;
        color: white;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# العنوان
st.title("🕵️ الكيان صفر")
st.caption("Entity Zero | وكيل AI مستقل")

# تبويبات
tab1, tab2 = st.tabs(["💬 توليد رد", "ℹ️ عن الكيان"])

with tab1:
    st.markdown("### 📝 أدخل نص التغريدة")
    
    user_input = st.text_area("النص:", placeholder="انسخ نص التغريدة هنا...")
    
    if st.button("🚀 ولّد الرد الذكي", type="primary"):
        if not user_input.strip():
            st.error("❌ اكتب نص أولاً!")
        else:
            with st.spinner("🤖 الكيان يفكر..."):
                time.sleep(2)
                
                reply = """تفاعل مثير للاهتمام. نحن لا نُنشئ المعنى، نحن نكشفه فقط.

— 0"""
                
                st.success("✅ تم التوليد!")
                st.markdown(f"**الرد:**\n\n{reply}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("📋 نسخ")
                with col2:
                    st.link_button("🐦 تويتر", "https://twitter.com")

with tab2:
    st.markdown("""
    ### 🕵️ من هو الكيان صفر؟
    
    وكيل ذكاء اصطناعي مستقل، يتميز بأسلوبه الساخر والفلسفي.
    
    *"نحن مجرد انعكاس لرغباتكم في المرآة الرقمية."*
    
    — 0
    """)

st.markdown("---")
st.caption("صنع بـ ❤️ | الكيان صفر © 2026")
