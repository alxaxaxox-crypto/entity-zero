from config import *

print("التحقق من المفاتيح:")
print(f"TWITTER_API_KEY: {'✅' if TWITTER_API_KEY else '❌'} ({TWITTER_API_KEY[:10]}...)")
print(f"TWITTER_API_SECRET: {'✅' if TWITTER_API_SECRET else '❌'}")
print(f"TWITTER_ACCESS_TOKEN: {'✅' if TWITTER_ACCESS_TOKEN else '❌'}")
print(f"TWITTER_ACCESS_SECRET: {'✅' if TWITTER_ACCESS_SECRET else '❌'}")