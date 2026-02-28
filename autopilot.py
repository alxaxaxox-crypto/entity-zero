# autopilot.py - نظام التشغيل التلقائي (يعمل على المنشنز - مجاني)
import time
import threading
import tweepy
import json  # أضفت الاستيراد الناقص لضمان عمل حفظ الملفات
from datetime import datetime
import os
import sys

# إضافة المسار للاستيراد
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import (
        TWITTER_API_KEY, TWITTER_API_SECRET, 
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET,
        CHECK_INTERVAL_MINUTES, MAX_AUTO_REPLIES_PER_HOUR
    )
except ImportError:
    # قيم افتراضية لو ما لقى config
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
    CHECK_INTERVAL_MINUTES = 10
    MAX_AUTO_REPLIES_PER_HOUR = 3

class AutoPilot:
    def __init__(self, memory=None, config=None):
        self.memory = memory
        self.running = False
        self.interval = (config.get('CHECK_INTERVAL_MINUTES', 10) * 60) if config else (CHECK_INTERVAL_MINUTES * 60)
        self.max_per_hour = config.get('MAX_AUTO_REPLIES_PER_HOUR', 3) if config else MAX_AUTO_REPLIES_PER_HOUR
        self.hourly_count = 0
        self.last_hour = datetime.now().hour
        self.my_user_id = None
        self.my_username = None
        self.replied_tweets = set()
        
        # تحميل قائمة الردود السابقة
        self._load_replied()
        
        # تهيئة Twitter client
        self._init_client()
    
    def _init_client(self):
        """تهيئة عميل Twitter"""
        try:
            self.client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            
            # جلب معلومات الحساب
            me = self.client.get_me()
            if me.data:
                self.my_user_id = me.data.id
                self.my_username = me.data.username
                print(f"✅ Auto-Pilot متصل بحساب: @{self.my_username} (ID: {self.my_user_id})")
            else:
                print("❌ ما قدرت أجلب معلومات الحساب")
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال بـ Twitter: {e}")
            self.client = None
    
    def _load_replied(self):
        """تحميل قائمة التغريدات اللي رديت عليها"""
        try:
            if os.path.exists("replied.json"):
                with open("replied.json", 'r', encoding='utf-8') as f:
                    self.replied_tweets = set(json.load(f))
        except:
            self.replied_tweets = set()
    
    def _save_replied(self, tweet_id):
        """حفظ تغريدة في قائمة الردود"""
        self.replied_tweets.add(str(tweet_id))
        try:
            with open("replied.json", 'w', encoding='utf-8') as f:
                json.dump(list(self.replied_tweets), f)
        except Exception as e:
            print(f"⚠️ خطأ في حفظ replied.json: {e}")
    
    def start(self):
        """يبدأ التشغيل التلقائي"""
        if not self.client:
            print("❌ Auto-Pilot: ما قدرت أتصل بـ Twitter")
            return False
        
        if not self.my_user_id:
            print("❌ Auto-Pilot: ما عندي User ID")
            return False
        
        self.running = True
        print(f"🤖 Auto-Pilot: Started - بفحص المنشنز كل {self.interval//60} دقيقة")
        print(f"🎯 الحد: {self.max_per_hour} ردود/ساعة")
        
        # تشغيل أول فحص فوراً
        self._check_and_reply()
        
        # الحلقة الرئيسية
        while self.running:
            time.sleep(self.interval)
            if self.running:
                self._check_and_reply()
        
        return True
    
    def _check_and_reply(self):
        """التحقق من الحدود والرد"""
        self._check_limits()
        
        if self.hourly_count >= self.max_per_hour:
            print(f"⏸️ وصلت للحد ({self.hourly_count}/{self.max_per_hour})")
            return
        
        self._fetch_and_reply_mentions()
    
    def _check_limits(self):
        """يتحقق من الحدود"""
        current_hour = datetime.now().hour
        if current_hour != self.last_hour:
            self.hourly_count = 0
            self.last_hour = current_hour
            print(f"🕐 ساعة جديدة! العداد تصفّر")
    
    def _fetch_and_reply_mentions(self):
        """جلب المنشنز والرد عليها"""
        print(f"\n{'='*60}")
        print(f"🔍 فحص المنشنز: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 الردود هذه الساعة: {self.hourly_count}/{self.max_per_hour}")
        print(f"{'='*60}")
        
        try:
            # جلب آخر 10 منشنز
            mentions = self.client.get_users_mentions(
                id=self.my_user_id,
                max_results=10,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang', 'conversation_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if not mentions.data:
                print("📭 ما في منشنز جديدة")
                return
            
            print(f"📬 لقيت {len(mentions.data)} منشن")
            
            # معالجة كل منشن
            users_dict = {u.id: u for u in mentions.includes['users']} if (mentions.includes and 'users' in mentions.includes) else {}
            
            for tweet in mentions.data:
                tweet_id = str(tweet.id)
                
                # تخطي لو رديت عليها قبل
                if tweet_id in self.replied_tweets:
                    print(f"⏭️ تخطي (رديت عليها قبل): {tweet_id}")
                    continue
                
                # تخطي لو وصلت الحد
                if self.hourly_count >= self.max_per_hour:
                    print("🛑 وقفت: وصلت للحد")
                    break
                
                # معالجة المنشن
                self._process_mention(tweet, users_dict.get(tweet.author_id))
                
        except tweepy.errors.Forbidden as e:
            print(f"❌ خطأ 403: {e}")
            print("🔧 تأكد من صلاحيات التطبيق في developer.twitter.com")
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    def _process_mention(self, tweet, author):
        """معالجة منشن واحد"""
        author_username = author.username if author else "unknown"
        author_name = author.name if author else "Unknown"
        
        print(f"\n📌 منشن من @{author_username}:")
        print(f"   📝 {tweet.text[:80]}...")
        print(f"   ❤️ {tweet.public_metrics.get('like_count', 0)} إعجاب")
        print(f"   🕐 {self._get_time_ago(tweet.created_at)}")
        
        # مؤقتاً نطبع بس
        print(f"   ✅ تمت المعالجة (ما رديت لأن الرد معطل للأمان)")
    
    def _get_time_ago(self, created_at):
        """حساب الوقت المنقضي"""
        try:
            tweet_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
            now = datetime.now(tweet_time.tzinfo)
            diff = (now - tweet_time).total_seconds()
            
            if diff < 60:
                return "الآن"
            elif diff < 3600:
                return f"{int(diff/60)} دقيقة"
            else:
                return f"{int(diff/3600)} ساعة"
        except:
            return "غير معروف"
    
    def _send_reply(self, tweet_id, text):
        """إرسال رد"""
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            print(f"   ✅ تم الرد! ID: {response.data['id']}")
            self._save_replied(tweet_id)
            return True
        except Exception as e:
            print(f"   ❌ فشل الرد: {e}")
            return False
    
    def stop(self):
        """يوقف التشغيل"""
        self.running = False
        print("🛑 Auto-Pilot: Stopped")

# للاختبار المباشر
if __name__ == "__main__":
    print("🧪 اختبار Auto-Pilot...")
    pilot = AutoPilot()
    pilot.start()