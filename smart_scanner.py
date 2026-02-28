# smart_scanner.py - ماسح ذكي متكامل
import time
import json
import os
import re
import requests
from datetime import datetime

# استيراد الإعدادات
try:
    from config import GROK_API_KEY, OLLAMA_URL, OLLAMA_MODEL, USE_OLLAMA
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("⚠️ Twitter API غير متاح")

class SmartScanner:
    def __init__(self):
        self.targets_file = "targets.txt"
        self.replied_file = "replied.json"
        self.replied = self._load_replied()
        self.client = None
        
        if TWITTER_AVAILABLE:
            try:
                from config import (
                    TWITTER_API_KEY, TWITTER_API_SECRET,
                    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
                )
                self.client = tweepy.Client(
                    consumer_key=TWITTER_API_KEY,
                    consumer_secret=TWITTER_API_SECRET,
                    access_token=TWITTER_ACCESS_TOKEN,
                    access_token_secret=TWITTER_ACCESS_SECRET
                )
                print("✅ متصل بـ Twitter API")
            except Exception as e:
                print(f"⚠️ ما قدرت أتصل بـ Twitter: {e}")

    def _load_replied(self):
        """تحميل قائمة الردود السابقة"""
        try:
            if os.path.exists(self.replied_file):
                with open(self.replied_file, 'r') as f:
                    return set(json.load(f))
        except Exception as e:
            print(f"⚠️ خطأ في تحميل الردود: {e}")
        return set()

    def _save_replied(self, tweet_id):
        """حفظ تغريدة تم الرد عليها"""
        self.replied.add(str(tweet_id))
        try:
            with open(self.replied_file, 'w') as f:
                json.dump(list(self.replied), f)
        except Exception as e:
            print(f"⚠️ خطأ في الحفظ: {e}")

    def _load_targets(self):
        """تحميل الأهداف من الملف"""
        if not os.path.exists(self.targets_file):
            with open(self.targets_file, 'w', encoding='utf-8') as f:
                f.write("# أضف روابط تويتر هنا\n")
            return []
        try:
            with open(self.targets_file, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                return lines
        except Exception as e:
            print(f"❌ خطأ في قراءة الأهداف: {e}")
            return []

    def _extract_tweet_id(self, url):
        """استخراج ID من الرابط"""
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _fetch_tweet_text(self, tweet_id):
        """جلب نص التغريدة من Twitter"""
        if not self.client:
            return None, None
        
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['text', 'lang'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if tweet.data:
                username = None
                if tweet.includes and 'users' in tweet.includes:
                    username = tweet.includes['users'][0].username
                
                return tweet.data.text, username
            return None, None
        except Exception as e:
            print(f"   ❌ ما قدرت أجلب التغريدة: {e}")
            return None, None

    def _generate_reply(self, text, lang="ar"):
        """توليد رد ذكي باستخدام Grok أو Ollama"""
        
        # نستخدم Grok إذا متاح
        if GROK_API_KEY and not USE_OLLAMA:
            try:
                headers = {
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "grok-3",
                    "messages": [{
                        "role": "user",
                        "content": f"رد باختصار على: {text[:200]}\n\nأسلوب: ساخر، فلسفي، 2-3 جمل، انتهِ بـ — 0"
                    }],
                    "temperature": 0.7,
                    "max_tokens": 150
                }
                
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers, json=data, timeout=20
                )
                
                if response.status_code == 200:
                    reply = response.json()["choices"][0]["message"]["content"]
                    if "— 0" not in reply:
                        reply += "\n\n— 0"
                    return reply
                    
            except Exception as e:
                print(f"   ⚠️ Grok فشل: {e}")
        
        # نرجع لـ Ollama
        if USE_OLLAMA:
            try:
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": f"رد على: {text[:200]}\n\nبأسلوب ساخر فلسفي، جملتين، انتهِ بـ — 0",
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 150}
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    reply = response.json()["response"]
                    if "— 0" not in reply:
                        reply += "\n\n— 0"
                    return reply
                    
            except Exception as e:
                print(f"   ⚠️ Ollama فشل: {e}")
        
        # رد افتراضي
        return "تفاعل مثير للاهتمام.\n\n— 0"

    def _send_reply(self, tweet_id, text):
        """إرسال الرد على تويتر"""
        if not self.client:
            print("   ❌ Twitter API غير متاح")
            return False
        
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            print(f"   ✅ تم الإرسال! ID: {response.data['id']}")
            return True
        except Exception as e:
            print(f"   ❌ فشل الإرسال: {e}")
            return False

    def scan_and_reply(self, mode="preview", delay=60):
        """
        المسح والرد الذكي
        
        mode: "preview" (عرض فقط), "generate" (توليد رد), "auto" (إرسال تلقائي)
        """
        targets = self._load_targets()
        if not targets:
            print("📭 ما في أهداف في targets.txt")
            return

        print(f"\n{'='*60}")
        print(f"🤖 Smart Scanner: {len(targets)} هدف")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        mode_names = {
            "preview": "معاينة فقط",
            "generate": "توليد رد (بدون إرسال)",
            "auto": "تلقائي (مع إرسال)"
        }
        print(f"🎯 الوضع: {mode_names.get(mode, 'معاينة')}")
        print(f"{'='*60}\n")

        for i, url in enumerate(targets, 1):
            tweet_id = self._extract_tweet_id(url)
            if not tweet_id:
                print(f"❌ [{i}] رابط غير صحيح: {url[:50]}...")
                continue

            if tweet_id in self.replied:
                print(f"⏭️ [{i}] تخطي (رديت قبل): {tweet_id}")
                continue

            print(f"\n{'─'*60}")
            print(f"🔍 [{i}/{len(targets)}] معالجة: {tweet_id}")
            print(f"🔗 {url}")

            # جلب نص التغريدة
            tweet_text, username = self._fetch_tweet_text(tweet_id)
            
            if tweet_text:
                print(f"   👤 @{username or 'unknown'}")
                print(f"   📝 {tweet_text[:100]}...")
                
                if mode in ["generate", "auto"]:
                    # توليد رد
                    print("   🤖 يولد الرد...")
                    reply = self._generate_reply(tweet_text)
                    print(f"   💬 الرد: {reply[:80]}...")
                    
                    if mode == "auto":
                        # إرسال تلقائي
                        if self._send_reply(tweet_id, reply):
                            self._save_replied(tweet_id)
                    else:
                        # وضع التوليد - نسأل المستخدم
                        confirm = input(f"   ❓ ترسل الرد؟ (y/n): ").lower().strip()
                        if confirm == 'y':
                            if self._send_reply(tweet_id, reply):
                                self._save_replied(tweet_id)
                else:
                    print("   👁️ وضع المعاينة")
            else:
                print("   ⚠️ ما قدرت أجلب النص")

            if i < len(targets):
                print(f"   ⏳ انتظر {delay} ثانية...")
                time.sleep(delay)

        print(f"\n{'='*60}")
        print(f"✅ انتهى! إجمالي الردود المخزنة: {len(self.replied)}")
        print(f"{'='*60}\n")

    def add_target(self, url):
        """إضافة رابط جديد للقائمة"""
        try:
            with open(self.targets_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{url}")
            print(f"✅ أضفت الهدف: {url}")
        except Exception as e:
            print(f"❌ فشل: {e}")

if __name__ == "__main__":
    scanner = SmartScanner()
    
    # اختر الوضع:
    # "preview" = عرض فقط
    # "generate" = توليد رد + سؤالك قبل الإرسال
    # "auto" = تلقائي بالكامل
    
    scanner.scan_and_reply(mode="generate", delay=5)