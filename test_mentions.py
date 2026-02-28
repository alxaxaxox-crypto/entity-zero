import tweepy
from config import *

client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# جرب طريقة ثانية - تحقق من المستخدم المسجل
try:
    # هذه تعمل على Free API عادة
    user = client.get_user(username="EntityZ31324")  # حط يوزرك هنا
    print(f"✅ متصل! User ID: {user.data.id}")
    
    # جرب المنشنز
    mentions = client.get_users_mentions(id=user.data.id, max_results=5)
    if mentions.data:
        print(f"📬 {len(mentions.data)} منشن")
        for m in mentions.data:
            print(f"  - {m.text[:50]}...")
    else:
        print("📭 ما في منشنز")
        
except Exception as e:
    print(f"❌ خطأ: {e}")
    print("\n🔧 جرب التحقق من:")
    print("1. هل المفاتيح صحيحة في .env؟")
    print("2. هل التطبيق مفعل في developer.twitter.com؟")
    print("3. هل صلاحياته 'Read and Write'؟")