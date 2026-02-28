import tkinter as tk
from tkinter import messagebox, ttk
import requests
import time
import re
import threading
import json
import os
from datetime import datetime

# استيراد الإعدادات
from config import (
    GROK_API_KEY, MAX_DAILY_REPLIES, MIN_DELAY_MINUTES, DELAY_SECONDS,
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET,
    USE_OLLAMA, OLLAMA_URL, OLLAMA_MODEL, OLLAMA_NUM_CTX,
    USE_MEMORY,
    USE_HYBRID_MODE, GROK_FOR_GENERATION, OLLAMA_FOR_TRAINING,
    AUTO_PILOT_ENABLED, CHECK_INTERVAL_MINUTES, MAX_AUTO_REPLIES_PER_HOUR
)
from prompts import get_prompt

# استيراد الذاكرة
if USE_MEMORY:
    from memory import SimpleMemory

# قيم افتراضية
REPLIED_FILE = "replied.json"
STATS_FILE = "stats.json"

# ===== Twitter API Setup (Tweepy) =====
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("⚠️ Tweepy not installed. Run: pip install tweepy")


class StatsManager:
    def __init__(self):
        self.request_count = 0
        self.last_request_time = 0
        self.replied_tweets = set()
        self.load_all()
    
    def load_all(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('date') == datetime.now().strftime("%Y-%m-%d"):
                        self.request_count = data.get('count', 0)
                        self.last_request_time = data.get('last_time', 0)
                    else:
                        self.reset_daily()
        except:
            self.reset_daily()
        
        try:
            if os.path.exists(REPLIED_FILE):
                with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
                    self.replied_tweets = set(json.load(f))
        except:
            self.replied_tweets = set()
    
    def save_all(self):
        try:
            data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "count": self.request_count,
                "last_time": self.last_request_time
            }
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving stats: {e}")
        
        try:
            with open(REPLIED_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(self.replied_tweets), f)
        except Exception as e:
            print(f"Error saving replied: {e}")
    
    def reset_daily(self):
        self.request_count = 0
        self.last_request_time = 0
        self.save_all()
    
    def can_make_request(self):
        if self.request_count >= MAX_DAILY_REPLIES:
            return False, f"⚠️ وصلت للحد اليومي ({MAX_DAILY_REPLIES})"
        
        if MIN_DELAY_MINUTES > 0:
            current_time = time.time()
            minutes_passed = (current_time - self.last_request_time) / 60
            
            if self.last_request_time > 0 and minutes_passed < MIN_DELAY_MINUTES:
                remaining = int(MIN_DELAY_MINUTES - minutes_passed)
                return False, f"⏳ انتظر {remaining} دقيقة"
        
        return True, ""
    
    def record_request(self, tweet_id=None):
        """تسجيل طلب جديد"""
        self.request_count += 1
        self.last_request_time = time.time()
        if tweet_id:
            self.replied_tweets.add(tweet_id)
        self.save_all()


class AutoPilot:
    """نظام التشغيل التلقائي - وكيل مستقل"""
    def __init__(self, gui):
        self.gui = gui
        self.running = False
        self.interval = CHECK_INTERVAL_MINUTES * 60
        self.max_per_hour = MAX_AUTO_REPLIES_PER_HOUR
        self.hourly_count = 0
        self.last_hour = datetime.now().hour
        self.thread = None
        self.target_keywords = ["AI", "ذكاء اصطناعي", "تكنولوجيا", "مستقبل", "وظائف"]
    
    def start(self):
        """بدء التشغيل التلقائي"""
        if not TWITTER_AVAILABLE:
            print("❌ Auto-Pilot: Twitter API غير متاح")
            return False
        
        if not AUTO_PILOT_ENABLED:
            print("❌ Auto-Pilot: معطل في الإعدادات")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"🤖 Auto-Pilot: Started (كل {CHECK_INTERVAL_MINUTES} دقيقة)")
        return True
    
    def stop(self):
        """إيقاف التشغيل التلقائي"""
        self.running = False
        print("🛑 Auto-Pilot: Stopped")
    
    def _run_loop(self):
        """الحلقة الرئيسية"""
        while self.running:
            try:
                self._check_limits()
                self._scan_and_reply()
                time.sleep(self.interval)
            except Exception as e:
                print(f"⚠️ Auto-Pilot Error: {e}")
                time.sleep(60)
    
    def _check_limits(self):
        """التحقق من الحدود"""
        current_hour = datetime.now().hour
        if current_hour != self.last_hour:
            self.hourly_count = 0
            self.last_hour = current_hour
            print(f"🕐 Auto-Pilot: Hour reset ({self.hourly_count}/{self.max_per_hour})")
    
    def _scan_and_reply(self):
        """فحص التغريدات والرد - مع طباعة تفصيلية"""
        if self.hourly_count >= self.max_per_hour:
            print(f"\n{'='*60}")
            print(f"⏸️ Auto-Pilot: Hourly limit reached ({self.hourly_count}/{self.max_per_hour})")
            print(f"{'='*60}\n")
            return
        
        print(f"\n{'='*60}")
        print(f"🤖 Auto-Pilot: Starting scan at {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 Stats: {self.hourly_count}/{self.max_per_hour} replies this hour")
        print(f"🔍 Keywords: {', '.join(self.target_keywords)}")
        print(f"{'='*60}")
        
        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            
            total_found = 0
            
            for keyword in self.target_keywords:
                if self.hourly_count >= self.max_per_hour:
                    print(f"\n⏹️ Stopped: Hourly limit reached")
                    break
                
                print(f"\n{'─'*60}")
                print(f"🔍 Searching for: '{keyword}'")
                print(f"{'─'*60}")
                
                try:
                    tweets = client.search_recent_tweets(
                        query=keyword,
                        max_results=10,
                        tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                        expansions=['author_id'],
                        user_fields=['username']
                    )
                    
                    if tweets.data:
                        print(f"✅ Found {len(tweets.data)} tweets about '{keyword}'")
                        total_found += len(tweets.data)
                        
                        for i, tweet in enumerate(tweets.data[:3], 1):
                            print(f"\n  📌 Tweet #{i}:")
                            print(f"     📝 Text: {tweet.text[:80]}...")
                            print(f"     👤 @{self._get_username(tweets, tweet.author_id)}")
                            print(f"     ❤️ {tweet.public_metrics['like_count']} likes")
                            print(f"     ⏰ {self._get_hours_ago(tweet.created_at):.1f} hours ago")
                            
                            if self._should_reply(tweet):
                                print(f"     ✅ WOULD REPLY (disabled for safety)")
                                # TODO: Implement actual reply logic here
                                # self._send_reply(client, tweet)
                            else:
                                print(f"     ❌ SKIP")
                                
                    else:
                        print(f"❌ No tweets found for '{keyword}'")
                        
                except Exception as e:
                    print(f"⚠️ Error: {str(e)}")
            
            print(f"\n{'='*60}")
            print(f"✅ Scan completed! Total: {total_found} tweets")
            print(f"⏰ Next scan in {CHECK_INTERVAL_MINUTES} minutes")
            print(f"{'='*60}\n")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def _get_username(self, tweets, author_id):
        """يستخرج اسم المستخدم"""
        if tweets.includes and 'users' in tweets.includes:
            for user in tweets.includes['users']:
                if user.id == author_id:
                    return user.username
        return "unknown"
    
    def _get_hours_ago(self, created_at):
        """يحسب عدد الساعات منذ التغريدة"""
        tweet_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
        return (datetime.now(tweet_time.tzinfo) - tweet_time).total_seconds() / 3600
    
    def _should_reply(self, tweet):
        """يقرر إذا يرد على التغريدة"""
        hours_ago = self._get_hours_ago(tweet.created_at)
        
        if hours_ago > 2:
            return False
        if tweet.public_metrics['like_count'] < 3:
            return False
        if tweet.lang not in ['ar', 'en']:
            return False
        
        return True


class EntityZeroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🕵️ Entity Zero - الكائن صفر")
        self.root.geometry("700x900")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)
        
        self.stats = StatsManager()
        self.current_tweet_id = None
        self.generated_reply = ""
        self.current_source = "unknown"
        
        # تهيئة الذاكرة
        self.memory = None
        if USE_MEMORY:
            try:
                self.memory = SimpleMemory()
                print(f"🧠 الذاكرة نشطة: {self.memory.get_stats()}")
            except Exception as e:
                print(f"⚠️ تعذر تحميل الذاكرة: {e}")
        
        # تهيئة Auto-Pilot
        self.autopilot = None
        if AUTO_PILOT_ENABLED:
            self.autopilot = AutoPilot(self)
        
        self.current_username = None
        
        self.setup_ui()
        self.update_counter()
        
        if USE_HYBRID_MODE and GROK_FOR_GENERATION:
            if not GROK_API_KEY or 'your' in GROK_API_KEY.lower():
                messagebox.showwarning("تنبيه", "Grok API Key غير مضبوط! سيتم استخدام Ollama.")
        
        if not TWITTER_AVAILABLE:
            messagebox.showwarning("تنبيه", "لازم تثبت tweepy عشان تقدر تغرد:\npip install tweepy")
    
    def setup_ui(self):
        # العنوان
        tk.Label(self.root, text="🕵️ Entity Zero", fg="#00ff00", bg="#0a0a0a", font=("Arial", 28, "bold")).pack(pady=10)
        tk.Label(self.root, text="وكيل AI مستقل | @EntityZ31324", fg="#666", bg="#0a0a0a", font=("Arial", 12)).pack()
        
        # وضع التشغيل
        mode_text = "🧠 الوضع: "
        if AUTO_PILOT_ENABLED:
            mode_text += "🤖 وكيل مستقل (Auto-Pilot)"
        elif USE_HYBRID_MODE:
            mode_text += "هجين (Grok + Ollama)"
        elif USE_OLLAMA:
            mode_text += "Ollama محلي"
        else:
            mode_text += "Grok API"
        
        tk.Label(self.root, text=mode_text, fg="#ff9800", bg="#0a0a0a", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.lbl_status = tk.Label(self.root, text="✅ جاهز", fg="#00ff00", bg="#0a0a0a", font=("Arial", 10))
        self.lbl_status.pack(pady=5)
        
        tk.Label(self.root, text="─" * 60, fg="#333", bg="#0a0a0a").pack()
        
        # === Auto-Pilot Controls ===
        if AUTO_PILOT_ENABLED and self.autopilot:
            autopilot_frame = tk.Frame(self.root, bg="#0a0a0a")
            autopilot_frame.pack(pady=10)
            
            self.btn_autopilot = tk.Button(
                autopilot_frame, 
                text="🤖 تشغيل الوكيل المستقل", 
                command=self.toggle_autopilot,
                bg="#ff5722", 
                fg="white", 
                font=("Arial", 12, "bold"),
                width=25,
                height=2
            )
            self.btn_autopilot.pack(side=tk.LEFT, padx=5)
            
            tk.Label(
                autopilot_frame, 
                text=f"⏱️ كل {CHECK_INTERVAL_MINUTES}د | 🎯 {MAX_AUTO_REPLIES_PER_HOUR}/ساعة",
                fg="#999",
                bg="#0a0a0a",
                font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=10)
        
        # === حقل رابط التغريدة ===
        tk.Label(self.root, text="🔗 رابط التغريدة (Tweet URL):", fg="#ff9800", bg="#0a0a0a", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.entry_url = tk.Entry(self.root, width=65, bg="#1a1a1a", fg="#00ff00", insertbackground="#00ff00", font=("Arial", 10))
        self.entry_url.pack(pady=5, ipady=3)
        self.add_context_menu(self.entry_url)
        
        # === نص التغريدة ===
        tk.Label(self.root, text="📝 نص التغريدة (انسخه هنا):", fg="white", bg="#0a0a0a", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.entry_text = tk.Entry(self.root, width=65, bg="#1a1a1a", fg="#00ff00", insertbackground="#00ff00", font=("Arial", 11))
        self.entry_text.pack(pady=5, ipady=5)
        self.add_context_menu(self.entry_text)
        
        # أزرار استخراج النص
        btn_frame = tk.Frame(self.root, bg="#0a0a0a")
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="🔍 استخراج النص من الرابط", command=self.fetch_tweet_text, 
                 bg="#2e7d32", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # اختيار اللغة
        options_frame = tk.Frame(self.root, bg="#0a0a0a")
        options_frame.pack(pady=5)
        
        self.var_lang = tk.StringVar(value="auto")
        tk.Radiobutton(options_frame, text="تلقائي", variable=self.var_lang, value="auto", bg="#0a0a0a", fg="white", selectcolor="#0d47a1").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(options_frame, text="عربي", variable=self.var_lang, value="ar", bg="#0a0a0a", fg="white", selectcolor="#0d47a1").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(options_frame, text="English", variable=self.var_lang, value="en", bg="#0a0a0a", fg="white", selectcolor="#0d47a1").pack(side=tk.LEFT, padx=5)
        
        # === أزرار الوضع الهجين ===
        if USE_HYBRID_MODE:
            hybrid_frame = tk.Frame(self.root, bg="#0a0a0a")
            hybrid_frame.pack(pady=5)
            
            tk.Button(hybrid_frame, text="🧠 توليد Grok (تعليم)", command=lambda: self.start_generation(force_grok=True), 
                     bg="#9333ea", fg="white", font=("Arial", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
            
            tk.Button(hybrid_frame, text="🤖 توليد Ollama (تطبيق)", command=lambda: self.start_generation(force_ollama=True), 
                     bg="#059669", fg="white", font=("Arial", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        
        # زر التوليد العادي
        self.btn_generate = tk.Button(self.root, text="🚀 ولّد الرد الذكي (تلقائي)", command=self.start_generation, 
                                     bg="#0d47a1", fg="white", font=("Arial", 12, "bold"), 
                                     width=25, height=2, cursor="hand2")
        self.btn_generate.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.root, length=500, mode='indeterminate')
        
        # === منطقة الرد ===
        tk.Label(self.root, text="📋 الرد المولّد:", fg="white", bg="#0a0a0a", font=("Arial", 11, "bold")).pack()
        
        self.result = tk.Text(self.root, height=6, width=65, bg="#1a1a1a", fg="#00ff00", 
                             font=("Consolas", 11), insertbackground="#00ff00", wrap=tk.WORD)
        self.result.pack(pady=10)
        self.result.insert(1.0, "سيظهر الرد هنا...")
        self.add_context_menu(self.result)
        
        # === أزرار التحكم ===
        control_frame = tk.Frame(self.root, bg="#0a0a0a")
        control_frame.pack(pady=10)
        
        self.btn_copy = tk.Button(control_frame, text="📋 نسخ فقط", command=self.copy_reply, 
                                 bg="#333", fg="white", font=("Arial", 11), width=15, state="disabled")
        self.btn_copy.pack(side=tk.LEFT, padx=5)
        
        self.btn_send = tk.Button(control_frame, text="🐦 إرسال الرد لتويتر", command=self.send_to_twitter, 
                                 bg="#1da1f2", fg="white", font=("Arial", 11, "bold"), 
                                 width=20, state="disabled")
        self.btn_send.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🗑️ مسح", command=self.clear_all, 
                 bg="#c62828", fg="white", font=("Arial", 11), width=12).pack(side=tk.LEFT, padx=5)
        
        # === أزرار التعلم ===
        if USE_HYBRID_MODE and OLLAMA_FOR_TRAINING:
            learning_frame = tk.Frame(self.root, bg="#0a0a0a")
            learning_frame.pack(pady=5)
            
            tk.Button(learning_frame, text="📊 تصدير بيانات التدريب", command=self.export_training_data, 
                     bg="#7c3aed", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(learning_frame, text="🎓 عرض إحصائيات التعلم", command=self.show_learning_stats, 
                     bg="#0ea5e9", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.root, text="─" * 60, fg="#333", bg="#0a0a0a").pack(pady=10)
        
        # العداد
        self.lbl_counter = tk.Label(self.root, text="", fg="#ff9800", bg="#0a0a0a", font=("Arial", 11, "bold"))
        self.lbl_counter.pack()
        
        self.lbl_stats = tk.Label(self.root, text="", fg="#666", bg="#0a0a0a", font=("Arial", 9))
        self.lbl_stats.pack(pady=5)
    
    def toggle_autopilot(self):
        """تشغيل/إيقاف الوكيل المستقل"""
        if not self.autopilot:
            return
        
        if self.autopilot.running:
            self.autopilot.stop()
            self.btn_autopilot.config(
                text="🤖 تشغيل الوكيل المستقل",
                bg="#ff5722"
            )
            self.lbl_status.config(text="⏹️ Auto-Pilot: متوقف", fg="#ff9800")
        else:
            success = self.autopilot.start()
            if success:
                self.btn_autopilot.config(
                    text="⏹️ إيقاف الوكيل المستقل",
                    bg="#c62828"
                )
                self.lbl_status.config(text="🤖 Auto-Pilot: يعمل...", fg="#00ff00")
            else:
                messagebox.showwarning("تنبيه", "تعذر تشغيل Auto-Pilot. تحقق من Twitter API.")
    
    def add_context_menu(self, widget):
        menu = tk.Menu(widget, tearoff=0, bg="#333", fg="white", activebackground="#0d47a1")
        menu.add_command(label="📋 لصق", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="✂️ قص", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="📄 نسخ", command=lambda: widget.event_generate("<<Copy>>"))
        widget.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
    
    def extract_tweet_id(self, url):
        try:
            patterns = [
                r'twitter\.com/\w+/status/(\d+)',
                r'x\.com/\w+/status/(\d+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except:
            return None
    
    def fetch_tweet_text(self):
        if not TWITTER_AVAILABLE:
            messagebox.showerror("خطأ", "لازم تثبت tweepy أولاً:\npip install tweepy")
            return
        
        url = self.entry_url.get().strip()
        tweet_id = self.extract_tweet_id(url)
        
        if not tweet_id:
            messagebox.showerror("خطأ", "الرابط غير صحيح.")
            return
        
        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            
            tweet = client.get_tweet(
                tweet_id, 
                tweet_fields=['text'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if tweet.data:
                self.current_username = None
                if tweet.includes and 'users' in tweet.includes:
                    self.current_username = tweet.includes['users'][0].username
                
                self.entry_text.delete(0, tk.END)
                self.entry_text.insert(0, tweet.data.text)
                self.current_tweet_id = tweet_id
                
                status_msg = f"✅ تم استخراج نص التغريدة {tweet_id}"
                if self.current_username:
                    status_msg += f" | @{self.current_username}"
                    if self.memory:
                        context = self.memory.get_user_context(self.current_username)
                        if context:
                            status_msg += " (🧠 له ذاكرة)"
                
                self.lbl_status.config(text=status_msg, fg="#00ff00")
            else:
                messagebox.showerror("خطأ", "ما لقيت التغريدة.")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"ما قدرت أجلب التغريدة:\n{str(e)}")
    
    def detect_lang(self, text):
        if not text.strip():
            return "ar"
        return "ar" if re.search(r'[\u0600-\u06FF]', text) else "en"
    
    def start_generation(self, force_grok=False, force_ollama=False):
        text = self.entry_text.get().strip()
        url = self.entry_url.get().strip()
        
        if not text:
            messagebox.showwarning("تنبيه", "اكتب نص التغريدة أو استخرجها من الرابط")
            return
        
        self.current_tweet_id = self.extract_tweet_id(url) if url else None
        
        can_proceed, message = self.stats.can_make_request()
        if not can_proceed:
            messagebox.showwarning("توقف", message)
            return
        
        self.btn_generate.config(text="⏳ يعالج...", state="disabled", bg="#666")
        
        use_grok = False
        if USE_HYBRID_MODE:
            if force_grok:
                use_grok = True
                self.lbl_status.config(text="🧠 Grok يولد...", fg="#9333ea")
            elif force_ollama:
                use_grok = False
                self.lbl_status.config(text="🤖 Ollama يولد...", fg="#059669")
            else:
                use_grok = GROK_FOR_GENERATION
                self.lbl_status.config(text="🔄 جاري التوليد...", fg="#ff9800")
        else:
            if USE_OLLAMA:
                self.lbl_status.config(text="🔄 جاري الاتصال بـ Ollama...", fg="#ff9800")
            else:
                self.lbl_status.config(text="🔄 جاري الاتصال بـ xAI...", fg="#ff9800")
        
        self.progress.pack(pady=5)
        self.progress.start()
        
        thread = threading.Thread(target=self.generate_reply, args=(text, use_grok))
        thread.daemon = True
        thread.start()
    
    def generate_reply(self, text, use_grok=False):
        try:
            time.sleep(DELAY_SECONDS)
            
            lang_choice = self.var_lang.get()
            if lang_choice == "auto":
                lang = self.detect_lang(text)
            else:
                lang = lang_choice
            
            memory_context = None
            if self.memory and self.current_username:
                memory_context = self.memory.get_user_context(self.current_username)
                if not memory_context:
                    similar = self.memory.get_similar_interactions(text)
                    if similar:
                        memory_context = "تذكر: هناك تفاعلات سابقة مشابهة.\n"
            
            if self.memory and not use_grok:
                grok_examples = self.memory.get_grok_masterpieces(text[:20], max_items=2)
                if grok_examples:
                    memory_context = memory_context or ""
                    memory_context += "\nأمثلة من ردود Grok السابقة:\n"
                    for ex in grok_examples:
                        memory_context += f"- سؤال: {ex['user_text'][:40]}... -> رد: {ex['bot_reply'][:40]}...\n"
            
            prompt = get_prompt(text, lang, memory_context)
            
            if USE_HYBRID_MODE and use_grok:
                self.current_source = "grok"
                
                headers = {
                    "Authorization": f"Bearer {GROK_API_KEY}", 
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "grok-3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 150
                }
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers, 
                    json=data, 
                    timeout=20
                )
                
                if response.status_code == 200:
                    reply = response.json()["choices"][0]["message"]["content"]
                    
                    if self.memory and OLLAMA_FOR_TRAINING:
                        self.memory.save_for_training(text, reply, lang)
                        print("💾 تم حفظ رد Grok لتدريب Ollama")
                
            else:
                self.current_source = "ollama"
                
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7, 
                            "num_predict": 150,
                            "num_ctx": OLLAMA_NUM_CTX
                        }
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    reply = response.json()["response"]
            
            # إنشاء FakeResponse للتوحيد بين المصادر
            class FakeResponse:
                def __init__(self, text, source, status_code=200):
                    self.status_code = status_code
                    self._text = text
                    self._source = source
                
                def json(self):
                    return {"choices": [{"message": {"content": self._text}}], "source": self._source}
            
            fake_response = FakeResponse(reply, self.current_source)
            self.root.after(0, lambda: self.handle_response(fake_response, lang))
            
        except Exception as e:
            if USE_HYBRID_MODE and use_grok:
                print(f"⚠️ Grok فشل ({str(e)}), نرجع لـ Ollama...")
                self.generate_reply(text, use_grok=False)
            else:
                self.root.after(0, lambda err=str(e): self.show_error("خطأ", err))
    
    def handle_response(self, response, lang="ar"):
        self.progress.stop()
        self.progress.pack_forget()
        
        try:
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                source = getattr(response, '_source', 'unknown')
                
                if "— 0" not in reply:
                    reply = reply.strip() + "\n\n— 0"
                
                self.generated_reply = reply
                self.result.delete(1.0, tk.END)
                self.result.insert(1.0, reply)
                
                if self.memory and self.current_tweet_id:
                    self.memory.save_interaction(
                        tweet_id=self.current_tweet_id,
                        username=self.current_username,
                        user_text=self.entry_text.get().strip(),
                        bot_reply=reply,
                        lang=lang,
                        source=source
                    )
                
                self.stats.record_request(self.current_tweet_id)
                self.update_counter()
                
                remaining = MAX_DAILY_REPLIES - self.stats.request_count
                self.btn_generate.config(text=f"🚀 ولّد (متبقي: {remaining})", state="normal", bg="#0d47a1")
                
                self.btn_copy.config(state="normal", bg="#0d47a1")
                if TWITTER_AVAILABLE and self.current_tweet_id:
                    self.btn_send.config(state="normal", bg="#1da1f2")
                elif not self.current_tweet_id:
                    self.btn_send.config(state="disabled", bg="#666", text="🚫 ألصق رابط التغريدة أولاً")
                else:
                    self.btn_send.config(state="disabled", bg="#666")
                
                source_emoji = "🧠" if source == "grok" else "🤖"
                source_name = "Grok" if source == "grok" else "Ollama"
                self.lbl_status.config(
                    text=f"✅ تم التوليد ({source_emoji} {source_name})! اضغط 'إرسال' للنشر", 
                    fg="#00ff00"
                )
                
            elif response.status_code == 400:
                error_msg = response.json().get('error', 'Bad Request')
                self.show_error("⚠️ خطأ 400", str(error_msg))
            elif response.status_code == 429:
                self.show_error("⚠️ تجاوز الحد", "انتظر قليلاً...")
            elif response.status_code == 401:
                self.show_error("⚠️ مفتاح خاطئ", "GROK_API_KEY غير صالح")
            else:
                error = response.json().get('error', {}).get('message', 'خطأ غير معروف')
                self.show_error(f"خطأ {response.status_code}", error)
                
        except Exception as e:
            self.show_error("خطأ معالجة", str(e))
    
    def export_training_data(self):
        if not self.memory:
            messagebox.showwarning("تنبيه", "الذاكرة غير مفعلة")
            return
        
        try:
            count = self.memory.export_for_ollama_training()
            messagebox.showinfo("نجاح", f"تم تصدير {count} عينة تدريب!")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التصدير: {str(e)}")
    
    def show_learning_stats(self):
        if not self.memory:
            messagebox.showwarning("تنبيه", "الذاكرة غير مفعلة")
            return
        
        stats = self.memory.get_stats()
        msg = f"""📊 إحصائيات التعلم:
        
📝 المحادثات: {stats['total_conversations']}
👤 المستخدمين: {stats['unique_users']}
🎯 روائع Grok: {stats['grok_masterpieces']}
🎓 عينات التدريب: {stats['training_samples']}
        
آخر تفاعل: {stats['last_interaction']}"""
        
        messagebox.showinfo("إحصائيات التعلم", msg)
    
    def send_to_twitter(self):
        if not TWITTER_AVAILABLE:
            messagebox.showerror("خطأ", "لازم تثبت tweepy:\npip install tweepy")
            return
        
        if not self.generated_reply:
            messagebox.showwarning("تنبيه", "ولّد الرد أولاً")
            return
        
        if not self.current_tweet_id:
            messagebox.showwarning("تنبيه", "حط رابط التغريدة في الحق اللي فوق")
            return
        
        self.btn_send.config(text="⏳ يرسل...", state="disabled", bg="#666")
        self.lbl_status.config(text="🔄 جاري النشر على تويتر...", fg="#ff9800")
        
        thread = threading.Thread(target=self._post_tweet)
        thread.daemon = True
        thread.start()
    
    def _post_tweet(self):
        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            
            response = client.create_tweet(
                text=self.generated_reply,
                in_reply_to_tweet_id=self.current_tweet_id
            )
            
            tweet_id = response.data['id']
            self.root.after(0, lambda: self._on_tweet_sent_success(tweet_id))
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self._on_tweet_sent_error(err))
    
    def _on_tweet_sent_success(self, tweet_id):
        self.btn_send.config(text="✅ تم الإرسال!", bg="#4caf50", state="disabled")
        self.lbl_status.config(text=f"✅ تم النشر! (ID: {tweet_id})", fg="#00ff00")
        messagebox.showinfo("نجاح", f"تم إرسال الرد بنجاح!\n\nTweet ID: {tweet_id}")
        
        self.root.after(3000, lambda: self.btn_send.config(
            text="🐦 إرسال الرد لتويتر", bg="#1da1f2", state="disabled"
        ))
    
    def _on_tweet_sent_error(self, error):
        self.btn_send.config(text="❌ فشل الإرسال", bg="#c62828", state="normal")
        self.lbl_status.config(text="❌ فشل النشر", fg="#c62828")
        messagebox.showerror("خطأ في النشر", f"ما قدرت أنشر الرد:\n\n{error}")
    
    def show_error(self, title, message):
        messagebox.showerror(title, message)
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_generate.config(text="🚀 ولّد الرد الذكي", state="normal", bg="#0d47a1")
        self.lbl_status.config(text="❌ فشل", fg="#c62828")
    
    def copy_reply(self):
        text = self.result.get(1.0, tk.END).strip()
        if text and text != "سيظهر الرد هنا...":
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.btn_copy.config(text="✅ تم النسخ!", bg="#4caf50")
            self.root.after(1500, lambda: self.btn_copy.config(text="📋 نسخ فقط", bg="#333"))
    
    def clear_all(self):
        self.entry_url.delete(0, tk.END)
        self.entry_text.delete(0, tk.END)
        self.result.delete(1.0, tk.END)
        self.result.insert(1.0, "سيظهر الرد هنا...")
        self.current_tweet_id = None
        self.current_username = None
        self.generated_reply = ""
        self.current_source = "unknown"
        self.btn_copy.config(state="disabled", bg="#333")
        self.btn_send.config(state="disabled", bg="#666", text="🐦 إرسال الرد لتويتر")
    
    def update_counter(self):
        remaining = MAX_DAILY_REPLIES - self.stats.request_count
        self.lbl_counter.config(text=f"📊 الردود اليوم: {self.stats.request_count}/{MAX_DAILY_REPLIES} (متبقي: {remaining})")
        last_time = "لا يوجد"
        if self.stats.last_request_time:
            last_time = datetime.fromtimestamp(self.stats.last_request_time).strftime("%H:%M:%S")
        self.lbl_stats.config(text=f"آخر رد: {last_time}")


def main():
    root = tk.Tk()
    app = EntityZeroGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()