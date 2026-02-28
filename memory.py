# memory.py - نظام الذاكرة الطويلة للكيان صفر
import json
import os
import time
from datetime import datetime

class SimpleMemory:
    """ذاكرة بسيطة مبنية على JSON (بدون مكتبات خارجية)"""
    
    def __init__(self, db_path="./memory_db"):
        self.db_path = db_path
        self.memory_file = os.path.join(db_path, "conversations.json")
        self.users_file = os.path.join(db_path, "users.json")
        self.training_file = os.path.join(db_path, "training_data.jsonl")  # جديد
        self.grok_replies_file = os.path.join(db_path, "grok_masterpieces.json")  # جديد
        
        # إنشاء المجلد إذا ما موجود
        os.makedirs(db_path, exist_ok=True)
        
        # تحميل البيانات
        self.conversations = self._load_json(self.memory_file, [])
        self.users = self._load_json(self.users_file, {})
        self.grok_replies = self._load_json(self.grok_replies_file, [])  # جديد
        
        # إنشاء ملف التدريب إذا مو موجود
        if not os.path.exists(self.training_file):
            open(self.training_file, 'w', encoding='utf-8').close()
    
    def _load_json(self, filepath, default):
        """تحميل ملف JSON أو رجع قيمة افتراضية"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default
    
    def _save_json(self, filepath, data):
        """حفظ بيانات لـ JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ الذاكرة: {e}")
    
    def save_interaction(self, tweet_id, username, user_text, bot_reply, lang="ar", source="unknown"):
        """حفظ تفاعل جديد مع مصدر الرد (Grok أو Ollama)"""
        timestamp = time.time()
        
        # 1. حفظ المحادثة
        conversation = {
            "id": f"{tweet_id}_{int(timestamp)}",
            "tweet_id": tweet_id,
            "username": username or "unknown",
            "user_text": user_text,
            "bot_reply": bot_reply,
            "lang": lang,
            "source": source,  # جديد: Grok أو Ollama
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.conversations.append(conversation)
        
        # 2. إذا الرد من Grok، حفظه كـ " masterpiece"
        if source == "grok":
            self.grok_replies.append({
                "user_text": user_text,
                "bot_reply": bot_reply,
                "lang": lang,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self._save_json(self.grok_replies_file, self.grok_replies)
            print(f"🎯 تم حفظ رد Grok كـ Masterpiece!")
        
        # 3. تحديث بيانات المستخدم
        if username:
            if username not in self.users:
                self.users[username] = {
                    "first_seen": timestamp,
                    "interactions_count": 0,
                    "preferred_lang": lang,
                    "mood_history": [],
                    "topics": []
                }
            
            user = self.users[username]
            user["last_seen"] = timestamp
            user["interactions_count"] += 1
            user["last_bot_reply"] = bot_reply
            
            # تحليل بسيط للموضوع
            topic = " ".join(user_text.split()[:3])
            user["topics"].append(topic)
            if len(user["topics"]) > 10:
                user["topics"].pop(0)
        
        # 4. حفظ للملفات
        self._save_json(self.memory_file, self.conversations)
        self._save_json(self.users_file, self.users)
        
        print(f"💾 تم حفظ التفاعل: @{username} -> {tweet_id} (المصدر: {source})")
    
    def save_for_training(self, user_text, bot_reply, lang="ar"):
        """حفظ زوج (سؤال/جواب) لتدريب Ollama"""
        training_item = {
            "prompt": user_text,
            "response": bot_reply,
            "lang": lang,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "quality_score": len(bot_reply)  # بسيط: الردود الأطول أحسن
        }
        
        # إلحاق للملف
        with open(self.training_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(training_item, ensure_ascii=False) + "\n")
        
        print(f"🎓 تم إضافة عينة تدريب: {user_text[:30]}...")
    
    def get_training_data(self, min_quality=50, max_items=100):
        """جلب بيانات التدريب عالية الجودة"""
        training_data = []
        try:
            with open(self.training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        item = json.loads(line.strip())
                        if item.get('quality_score', 0) >= min_quality:
                            training_data.append(item)
                    except:
                        continue
        except:
            pass
        
        # رجع الأحدث والأفضل
        return sorted(training_data, key=lambda x: x.get('quality_score', 0), reverse=True)[:max_items]
    
    def get_grok_masterpieces(self, topic=None, max_items=5):
        """جلب ردود Grok الأفضل (لتعلم Ollama)"""
        if not self.grok_replies:
            return []
        
        if topic:
            # فلترة حسب الموضوع
            filtered = [
                r for r in self.grok_replies 
                if topic.lower() in r['user_text'].lower()
            ]
            return filtered[-max_items:]
        
        # رجع الأحدث
        return self.grok_replies[-max_items:]
    
    def get_user_context(self, username, max_items=3):
        """جلب سياق المستخدم السابق"""
        if not username or username not in self.users:
            return None
        
        user = self.users[username]
        
        user_conversations = [
            c for c in reversed(self.conversations) 
            if c["username"] == username
        ][:max_items]
        
        if not user_conversations:
            return None
        
        context = f"المستخدم @{username} تفاعل معك {user['interactions_count']} مرة سابقاً.\n"
        context += f"آخر مواضيع: {', '.join(user['topics'][-3:])}\n"
        context += "آخر ردودك له:\n"
        
        for i, conv in enumerate(user_conversations[:2], 1):
            context += f"{i}. هو قال: '{conv['user_text'][:50]}...' -> أنت رديت: '{conv['bot_reply'][:50]}...'\n"
        
        return context
    
    def get_similar_interactions(self, text, max_results=2):
        """البحث عن تفاعلات مشابهة"""
        words = set(text.lower().split())
        matches = []
        
        for conv in reversed(self.conversations[-100:]):
            conv_words = set(conv["user_text"].lower().split())
            common = words & conv_words
            
            if len(common) >= 2:
                matches.append((len(common), conv))
        
        matches.sort(reverse=True)
        return [m[1] for m in matches[:max_results]]
    
    def get_stats(self):
        """إحصائيات الذاكرة"""
        training_count = 0
        try:
            with open(self.training_file, 'r', encoding='utf-8') as f:
                training_count = sum(1 for _ in f if _.strip())
        except:
            pass
        
        return {
            "total_conversations": len(self.conversations),
            "unique_users": len(self.users),
            "grok_masterpieces": len(self.grok_replies),
            "training_samples": training_count,
            "last_interaction": self.conversations[-1]["date"] if self.conversations else "لا يوجد"
        }
    
    def export_for_ollama_training(self, output_file="./memory_db/ollama_train.txt"):
        """تصدير بيانات التدريب بصيغة Ollama Modelfile"""
        training_data = self.get_training_data(min_quality=30, max_items=200)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Training data for Ollama fine-tuning\n\n")
            for item in training_data:
                f.write(f"### User: {item['prompt']}\n")
                f.write(f"### Assistant: {item['response']}\n\n")
        
        print(f"📤 تم تصدير {len(training_data)} عينة لـ Ollama: {output_file}")
        return len(training_data)