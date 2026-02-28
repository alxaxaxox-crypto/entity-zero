# ==========================================
# ملف الإعدادات - آمن مع python-dotenv
# ==========================================

import os
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

# ----- مفاتيح Twitter API v2 -----
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

# ----- مفتاح Grok API (xAI) -----
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# ----- إعدادات الحماية (Rate Limits) -----
MAX_DAILY_REPLIES = 50         
MIN_DELAY_MINUTES = 0         
DELAY_SECONDS = 0             

# ----- إعدادات Ollama (محلي) -----
USE_OLLAMA = True              
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:3b"    
OLLAMA_NUM_CTX = 2048          

# ----- إعدادات الذاكرة الطويلة -----
USE_MEMORY = True              
MEMORY_DB_PATH = "./memory_db"

# ----- إعدادات التعلم المشترك -----
USE_HYBRID_MODE = True         
GROK_FOR_GENERATION = True     
OLLAMA_FOR_TRAINING = True     

# ----- إعدادات Auto-Pilot -----
AUTO_PILOT_ENABLED = True      
CHECK_INTERVAL_MINUTES = 10    
MAX_AUTO_REPLIES_PER_HOUR = 3  

# ----- التحقق من المفاتيح -----
def check_keys():
    """يتحقق إذا المفاتيح محملة بشكل صحيح"""
    missing = []
    if not TWITTER_API_KEY:
        missing.append("TWITTER_API_KEY")
    if not TWITTER_API_SECRET:
        missing.append("TWITTER_API_SECRET")
    if not GROK_API_KEY:
        missing.append("GROK_API_KEY")
    
    if missing:
        print(f"⚠️ تنبيه: المفاتيح التالية ناقصة: {', '.join(missing)}")
        print("🔧 تأكد من وجود ملف .env في نفس المجلد")
        return False
    return True

# تشغيل التحقق عند الاستيراد
KEYS_VALID = check_keys()