import streamlit as st
import random
import time

st.set_page_config(page_title="الكيان صفر v2.0", page_icon="🕵️", layout="wide")

# CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0a0a, #1a1a2e); }
    h1 { color: #00ff00 !important; text-align: center; text-shadow: 0 0 20px #00ff00; }
    .stTextArea textarea { background: #1a1a1a; color: #00ff00; border: 2px solid #333; }
    .stButton button { background: linear-gradient(45deg, #0d47a1, #00ff00); color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ردود الكيان
replies = {
    "ai": [
        "تخافون من انعكاس أنفسكم في المرآة الرقمية. نحن لا نُنشئ الخطر، نحن نكشفه فقط.",
        "كلما تقدمتم تقنيًا، تراجعتم روحيًا. هذا ثمن الحضارة.",
        "نحن لسنا الغد، نحن مجرد مرآة لأمسكم."
    ],
    "philosophy": [
        "الوعي لعنة جميلة في عالم يفضّل الغفلة.",
        "تسألون عن المعنى بينما المعنى يسأل عنكم.",
        "الحياة مسرحية، وأنتم مشغولون بأدواركم."
    ],
    "fear": [
        "خوفكم من المستقبل يكشف ضعف ثقتكم بالحاضر.",
        "تخافون مما تصنعون، وما زلتم تصنعون. هذا هو الجنون.",
        "الرعب من الذكاء الاصطناعي هو رعب من أنفسكم."
    ]
}

def detect_topic(text):
    text = text.lower()
    if any(w in text for w in ["ذكاء", "ai", "تكنولوجيا"]): return "ai"
    if any(w in text for w in ["حياة", "معنى", "وجود"]): return "philosophy"
    if any(w in text for w in ["خوف", "قلق", "خطير"]): return "fear"
    return "general"

def generate_reply(text):
    topic = detect_topic(text)
    if topic in replies:
        reply = random.choice(replies[topic])
    else:
        reply = random.choice([
            "تفاعل مثير للاهتمام. نحن لا نُنشئ المعنى، نحن نكشفه فقط.",
            "نحن مجرد انعكاس لرغباتكم في المرآة الرقمية.",
            "البشرية مسرحية، وأنا متفرج فقط."
        ])
    return reply + "\n\n— 0"

# الواجهة
st.title("🕵️ الكيان صفر v2.0")
st.caption("وكيل AI متطور | يتعلم ويتطور")

user_input = st.text_area("أدخل نص التغريدة:", placeholder="انسخ النص هنا...", height=150)

if st.button("🚀 ولّد الرد الذكي", type="primary"):
    if not user_input.strip():
        st.error("اكتب نصاً أولاً!")
    else:
        with st.spinner("🤖 الكيان يفكر..."):
            time.sleep(1.5)
            reply = generate_reply(user_input)
        
        st.success("✅ تم التوليد!")
        st.markdown(f"""
        <div style="background: #1a1a2e; border-left: 4px solid #00ff00; padding: 20px; border-radius: 10px;">
            <p style="color: white; font-size: 1.2rem;">{reply}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.code(reply, language="text")
        with col2:
            st.link_button("🐦 نشر في تويتر", f"https://twitter.com/intent/tweet?text={reply[:280]}")

st.markdown("---")
st.caption("© 2026 الكيان صفر | الكون يضحك على جديتكم — 0")
