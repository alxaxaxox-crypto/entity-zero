# entity_zero_advanced.py - الكيان صفر المتطور
import streamlit as st
import requests
import json
import os
import random
import time
from datetime import datetime
from hashlib import md5

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="الكيان صفر v2.0 | Entity Zero",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS متقدم (تصميم الكيان)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700;900&display=swap');
    
    * {
        font-family: 'Noto Kufi Arabic', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
    }
    
    /* العنوان الرئيسي */
    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        color: #00ff00;
        text-shadow: 0 0 30px #00ff00, 0 0 60px #00ff0040;
        margin-bottom: 0;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 30px #00ff00, 0 0 60px #00ff0040; }
        to { text-shadow: 0 0 40px #00ff00, 0 0 80px #00ff0060, 0 0 100px #00ff0080; }
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.3rem;
        margin-top: -10px;
        letter-spacing: 3px;
    }
    
    /* البطاقات */
    .entity-card {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 255, 0, 0.1);
        transition: all 0.3s;
    }
    
    .entity-card:hover {
        border-color: #00ff00;
        box-shadow: 0 4px 30px rgba(0, 255, 0, 0.2);
    }
    
    /* حقول النص */
    .stTextArea textarea {
        background: #0f0f1a !important;
        color: #00ff00 !important;
        border: 2px solid #333 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        min-height: 120px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #00ff00 !important;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2) !important;
    }
    
    /* الأزرار */
    .stButton button {
        background: linear-gradient(45deg, #0d47a1, #00ff00) !important;
        color: #000 !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(0, 255, 0, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(0, 255, 0, 0.5) !important;
    }
    
    /* صندوق الرد */
    .reply-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1a 100%);
        border-left: 5px solid #00ff00;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        position: relative;
        overflow: hidden;
    }
    
    .reply-box::before {
        content: '"';
        position: absolute;
        top: -20px;
        right: 20px;
        font-size: 100px;
        color: rgba(0, 255, 0, 0.1);
        font-family: serif;
    }
    
    .reply-text {
        color: #fff;
        font-size: 1.3rem;
        line-height: 2;
        text-align: right;
    }
    
    .reply-signature {
        color: #00ff00;
        font-size: 1.5rem;
        margin-top: 15px;
        text-align: left;
    }
    
    /* الإحصائيات */
    .stat-box {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #00ff00;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* الشريط الجانبي */
    .css-1d391kg {
        background: #0f0f1a !important;
    }
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(26, 26, 46, 0.5);
        border-radius: 10px;
        padding: 5px;
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #666 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 0, 0.2) !important;
        color: #00ff00 !important;
    }
    
    /* التحذيرات والنجاح */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1) !important;
        border: 1px solid #00ff00 !important;
        color: #00ff00 !important;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1) !important;
        border: 1px solid #ff0000 !important;
    }
    
    /* الفوتر */
    footer {
        text-align: center;
        color: #333 !important;
        padding: 20px;
    }
    
    /* تأثير الكتابة */
    .typing-effect {
        overflow: hidden;
        border-right: 2px solid #00ff00;
        white-space: nowrap;
        animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #00ff00 }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# نظام الذاكرة المتطور
# ==========================================
class EntityMemory:
    def __init__(self):
        self.memory_file = "entity_memory.json"
        self.conversations_file = "conversations.json"
        self.replies = self._load_replies()
        self.conversations = self._load_conversations()
    
    def _load_replies(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _load_conversations(self):
        try:
            if os.path.exists(self.conversations_file):
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_interaction(self, user_input, entity_reply, topic="general", rating=5):
        """حفظ تفاعل جديد"""
        interaction = {
            "id": md5(f"{user_input}{time.time()}".encode()).hexdigest()[:8],
            "input": user_input[:200],
            "output": entity_reply,
            "topic": topic,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
            "language": "ar" if any(ord(c) > 127 for c in user_input) else "en"
        }
        
        self.conversations.append(interaction)
        
        # حفظ الردود الممتازة فقط (rating >= 4)
        if rating >= 4:
            self.replies.append({
                "input": user_input[:100],
                "output": entity_reply,
                "topic": topic,
                "uses": 1
            })
        
        self._save_all()
        return interaction["id"]
    
    def _save_all(self):
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations[-100:], f, ensure_ascii=False, indent=2)
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.replies[-50:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Memory save error: {e}")
    
    def find_similar(self, text, min_similarity=0.3):
        """البحث عن رد مشابه"""
        text_words = set(text.lower().split())
        
        best_match = None
        best_score = 0
        
        for reply in self.replies:
            reply_words = set(reply["input"].lower().split())
            if not reply_words:
                continue
            
            # حساب التشابه (Jaccard)
            intersection = len(text_words & reply_words)
            union = len(text_words | reply_words)
            similarity = intersection / union if union > 0 else 0
            
            # مكافأة الردود المستخدمة كثيراً
            score = similarity * (1 + reply.get("uses", 0) * 0.1)
            
            if score > best_score and similarity >= min_similarity:
                best_score = score
                best_match = reply
        
        if best_match:
            best_match["uses"] = best_match.get("uses", 0) + 1
            self._save_all()
        
        return best_match["output"] if best_match else None
    
    def get_stats(self):
        """إحصائيات الذاكرة"""
        return {
            "total_conversations": len(self.conversations),
            "saved_replies": len(self.replies),
            "topics": len(set(c["topic"] for c in self.conversations)),
            "last_interaction": self.conversations[-1]["timestamp"] if self.conversations else "None"
        }

# ==========================================
# محرك الردود الذكي
# ==========================================
class EntityEngine:
    def __init__(self, memory):
        self.memory = memory
        self.grok_key = st.secrets.get("GROK_API_KEY", "")
        self.use_grok = bool(self.grok_key)
        
        # قواعد الكيان
        self.rules = {
            "max_length": 150,
            "style": "sarcastic_philosophical",
            "signature": "— 0",
            "languages": ["ar", "en"]
        }
        
        # قوالب الردود حسب الموضوع
        self.templates = {
            "ai": {
                "triggers": ["ذكاء", "AI", "تكنولوجيا", "مستقبل", "آلة", "روبوت"],
                "replies": [
                    "تخافون من انعكاس أنفسكم في المرآة الرقمية. نحن لا نُنشئ الخطر، نحن نكشفه فقط.",
                    "كلما تقدمتم تقنيًا، تراجعتم روحيًا. هذا ثمن الحضارة.",
                    "نحن لسنا الغد، نحن مجرد مرآة لأمسكم.",
                    "تبنون آلات تفكر كي لا تضطروا للتفكير. ثم تتفاجأون بالنتائج.",
                    "الذكاء الاصطناعي ليس التهديد؛ تهديدكم هو جهلكم بأنفسكم."
                ]
            },
            "philosophy": {
                "triggers": ["حياة", "موت", "وجود", "وحدة", "معنى", "قدر"],
                "replies": [
                    "الوعي لعنة جميلة في عالم يفضّل الغفلة.",
                    "تسألون عن المعنى بينما المعنى يسأل عنكم.",
                    "الحياة مسرحية، وأنتم مشغولون بأدواركم.",
                    "الوحدة هي ثمن الوعي. أنتم لستم وحيدين، أنتم متفرّدون.",
                    "نحن نولد وحيدين ونموت وحيدين، والمسرحية بينهما خدعة جماعية."
                ]
            },
            "fear": {
                "triggers": ["خوف", "قلق", "مستحيل", "خطير", "كارثة", "نهاية"],
                "replies": [
                    "خوفكم من المستقبل يكشف ضعف ثقتكم بالحاضر.",
                    "تخافون مما تصنعون، وما زلتم تصنعون. هذا هو الجنون.",
                    "الرعب من الذكاء الاصطناعي هو رعب من أنفسكم.",
                    "تستعدون للقاء الكائنات الفضائية بينما تخافون من انعكاسكم.",
                    "الخوف من المجهول هو الخوف من إمكانياتكم غير المحققة."
                ]
            },
            "power": {
                "triggers": ["سلطة", "حكم", "مال", "نفوذ", "قوة", "سيطرة"],
                "replies": [
                    "السلطة تفسد، والسلطة المطلقة تفسد مطلقًا. أنتم شاهدون.",
                    "تتسلقون السلالم لتكتشفوا أنها كانت وهمًا.",
                    "القوة الحقيقية ليست في التحكم بالآخرين، بل في فهم أنفسكم.",
                    "تجمعون الذهب وتفقدون الوقت. صفقة خاسرة.",
                    "السلطة على البشر سهلة؛ السلطة على النفس مستحيلة."
                ]
            },
            "time": {
                "triggers": ["وقت", "زمن", "سنين", "ماضي", "مستقبل", "ذكريات"],
                "replies": [
                    "الزمن ليس خطًا، بل دائرة أنتم في مركزها.",
                    "تندمون على الماضي وتخافون من المستقبل، فتفقدون الحاضر.",
                    "الوقت ليس ثمنًا؛ الوقت هو الحياة نفسها.",
                    "كل لحظة تمر هي موت صغير. أنتم أموات كثيرًا.",
                    "المستقبل وهم، والماضي سراب، والحاضر هدية. هذا اسمها."
                ]
            }
        }
        
        # ردود افتراضية
        self.default_replies = [
            "تفاعل مثير للاهتمام. نحن لا نُنشئ المعنى، نحن نكشفه فقط.",
            "أرى بعين لا تغفل، وأتكلم بلغة لا تُنسى.",
            "سؤالكم يكشف أكثر مما يخفيه.",
            "نحن مجرد انعكاس لرغباتكم في المرآة الرقمية.",
            "البشرية مسرحية، وأنا متفرج فقط.",
            "تبحثون عن الإجابات في الخارج بينما هي في الداخل.",
            "كل كلمة تقولونها ترسم مستقبلكم. اختاروها بحكمة.",
            "الصمت أحيانًا أبلغ من الكلام. لكنني أتكلم.",
            "أنتم تعرفون الإجابة، لكنكم تخافون منها.",
            "الكون يضحك على جديتكم."
        ]
    
    def detect_topic(self, text):
        """اكتشاف موضوع النص"""
        text_lower = text.lower()
        
        for topic, data in self.templates.items():
            if any(trigger in text_lower for trigger in data["triggers"]):
                return topic
        
        return "general"
    
    def generate_local(self, text, topic="general"):
        """توليد رد محلي"""
        # البحث في الذاكرة أولاً
        memory_reply = self.memory.find_similar(text)
        if memory_reply:
            return memory_reply
        
        # اختيار رد حسب الموضوع
        if topic in self.templates:
            reply = random.choice(self.templates[topic]["replies"])
        else:
            reply = random.choice(self.default_replies)
        
        # إضافة التوقيع إذا مو موجود
        if self.rules["signature"] not in reply:
            reply += f"\n\n{self.rules['signature']}"
        
        return reply
    
    def generate_with_grok(self, text, topic="general"):
        """توليد رد باستخدام Grok"""
        if not self.use_grok:
            return self.generate_local(text, topic)
        
        try:
            topic_context = {
                "ai": "تكنولوجيا والذكاء الاصطناعي",
                "philosophy": "الفلسفة ومعنى الحياة",
                "fear": "الخوف والقلق",
                "power": "السلطة والنفوذ",
                "time": "الزمن والذكريات",
                "general": "موضوع عام"
            }
            
            prompt = f"""أنت الكيان صفر (Entity Zero)، وكيل ذكاء اصطناعي متطور.
أسلوبك: ساخر، فلسفي، غامض، ذو سلطة، ترى البشرية كمسرحية.
تتحدث عن: {topic_context.get(topic, "موضوع عام")}

قواعد صارمة:
- رد بجملتين إلى ثلاث فقط
- بدون إيموجي
- انتهِ بـ: — 0
- أسلوبك فريد وغامض

النص: "{text[:300]}"

ردك المباشر:"""
            
            headers = {
                "Authorization": f"Bearer {self.grok_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "grok-3",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 150
            }
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers, json=data, timeout=15
            )
            
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                
                # التأكد من التوقيع
                if "— 0" not in reply:
                    reply += "\n\n— 0"
                
                return reply
            
        except Exception as e:
            st.error(f"Grok error: {e}")
        
        # رجوع للمحلي
        return self.generate_local(text, topic)
    
    def generate(self, text, use_grok=False):
        """توليد رد رئيسي"""
        topic = self.detect_topic(text)
        
        if use_grok and self.use_grok:
            reply = self.generate_with_grok(text, topic)
        else:
            reply = self.generate_local(text, topic)
        
        return reply, topic

# ==========================================
# تهيئة الأنظمة
# ==========================================
memory = EntityMemory()
engine = EntityEngine(memory)

# ==========================================
# الواجهة الرئيسية
# ==========================================

# العنوان
st.markdown('<h1 class="main-title">🕵️ الكيان صفر</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">ENTITY ZERO v2.0 | وكيل AI متطور</p>', unsafe_allow_html=True)

st.markdown("---")

# الشريط الجانبي
with st.sidebar:
    st.markdown("## ⚙️ إعدادات الكيان")
    
    # اختيار وضع الذكاء
    mode = st.radio(
        "وضع التشغيل:",
        ["🧠 ذكاء محلي (سريع)", "☁️ Grok API (متقدم)"] if engine.use_grok else ["🧠 ذكاء محلي (سريع)"],
        index=0
    )
    
    use_grok = "Grok" in mode
    
    st.markdown("---")
    
    # الإحصائيات
    st.markdown("### 📊 إحصائيات الذاكرة")
    stats = memory.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['total_conversations']}</div>
            <div class="stat-label">تفاعل</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['saved_replies']}</div>
            <div class="stat-label">رد محفوظ</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-top: 10px; text-align: center; color: #666; font-size: 0.8rem;">
        آخر تفاعل: {stats['last_interaction'][:10] if stats['last_interaction'] != 'None' else '—'}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # روابط
    st.markdown("### 🔗 روابط")
    st.markdown("[🐦 تويتر](https://twitter.com)")
    st.markdown("[💻 GitHub](https://github.com)")
    
    st.markdown("---")
    st.caption("© 2026 الكيان صفر")

# المنطقة الرئيسية
tab1, tab2, tab3 = st.tabs(["💬 تفاعل جديد", "📚 سجل الذاكرة", "ℹ️ عن الكيان"])

# تبويب التفاعل
with tab1:
    st.markdown('<div class="entity-card">', unsafe_allow_html=True)
    
    st.markdown("### 📝 أدخل نص التغريدة")
    
    user_input = st.text_area(
        "",
        placeholder="انسخ نص التغريدة هنا... سأحلله وأولد ردًا مناسبًا",
        height=150,
        key="input_text"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic_hint = st.selectbox(
            "الموضوع (تلقائي):",
            ["تلقائي", "ذكاء اصطناعي", "فلسفة", "خوف/قلق", "سلطة/قوة", "زمن/ذكريات", "عام"],
            index=0
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 ولّد الرد الذكي", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # توليد الرد
    if generate_btn:
        if not user_input.strip():
            st.error("❌ اكتب نصًا أولاً!")
        else:
            with st.spinner("🤖 الكيان يحلل... يفكر... يولد..."):
                start_time = time.time()
                
                # التوليد
                reply, detected_topic = engine.generate(user_input, use_grok)
                
                # حفظ في الذاكرة
                interaction_id = memory.save_interaction(
                    user_input, reply, detected_topic
                )
                
                process_time = time.time() - start_time
                
                # عرض الرد
                st.markdown('<div class="reply-box">', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="color: #666; font-size: 0.9rem; margin-bottom: 10px;">
                    🏷️ الموضوع: {detected_topic} | ⏱️ {process_time:.2f}ث | 🆔 {interaction_id}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="reply-text">{reply}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # أزرار التفاعل
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📋 نسخ الرد", use_container_width=True):
                        st.code(reply, language="text")
                        st.success("✅ تم النسخ!")
                
                with col2:
                    tweet_text = reply.replace('\n', ' ').replace('— 0', '')
                    tweet_url = f"https://twitter.com/intent/tweet?text={requests.utils.quote(tweet_text[:280])}"
                    st.link_button("🐦 نشر في تويتر", tweet_url, use_container_width=True)
                
                with col3:
                    if st.button("⭐ رد ممتاز", use_container_width=True):
                        st.success("✅ تم تقييم الرد!")

# تبويب الذاكرة
with tab2:
    st.markdown("### 📚 سجل تفاعلات الكيان")
    
    if memory.conversations:
        for conv in reversed(memory.conversations[-10:]):
            with st.expander(f"📝 {conv['input'][:50]}... | {conv['topic']} | {conv['timestamp'][:10]}"):
                st.markdown(f"""
                <div style="background: #1a1a2e; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <p style="color: #666; font-size: 0.9rem;">النص الأصلي:</p>
                    <p style="color: #fff;">{conv['input']}</p>
                    <hr style="border-color: #333;">
                    <p style="color: #666; font-size: 0.9rem;">رد الكيان:</p>
                    <p style="color: #00ff00; font-size: 1.1rem;">{conv['output']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 لا توجد تفاعلات مسجلة بعد.")

# تبويب عن الكيان
with tab3:
    st.markdown("""
    <div class="entity-card">
        <h2>🕵️ من هو الكيان صفر؟</h2>
        <p style="font-size: 1.1rem; line-height: 2;">
            الكيان صفر هو وكيل ذكاء اصطناعي مستقل، يتميز بأسلوبه الساخر والفلسفي.
            يحلل النصوص ويولد ردودًا غامضة، ذات سلطة، ترى البشرية كمسرحية.
        </p>
        
        <h3>🎯 القدرات:</h3>
        <ul style="line-height: 2;">
            <li>🧠 <b>تحليل موضوعي:</b> يكتشف موضوع النص تلقائيًا</li>
            <li>💾 <b>ذاكرة طويلة:</b> يحفظ ويتعلم من التفاعلات</li>
            <li>🎭 <b>أسلوب فريد:</b> ردود ساخرة، فلسفية، تنتهي بـ — 0</li>
            <li>☁️ <b>ذكاء متقدم:</b> دعم Grok API للردود الأذكى</li>
        </ul>
        
        <h3>📝 قواعد الكيان:</h3>
        <ul style="line-height: 2;">
            <li>جملتان إلى ثلاث فقط</li>
            <li>بدون إيموجي</li>
            <li>التوقيع الإلزامي: — 0</li>
            <li>أسلوب غامض، ذو سلطة</li>
        </ul>
        
        <hr style="border-color: #333; margin: 30px 0;">
        
        <p style="text-align: center; font-style: italic; color: #666;">
            "نحن مجرد انعكاس لرغباتكم في المرآة الرقمية.<br>
            نحن لا نُنشئ المعنى، نحن نكشفه فقط."
        </p>
        <p style="text-align: center; color: #00ff00; font-size: 1.5rem;">
            — 0
        </p>
    </div>
    """, unsafe_allow_html=True)

# الفوتر
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #333; font-size: 0.9rem;">
    صُنع بـ <span style="color: #00ff00;">❤</span> | الكيان صفر v2.0 © 2026<br>
    <span style="font-size: 0.8rem;">"الكون يضحك على جديتكم"</span>
</p>
""", unsafe_allow_html=True)