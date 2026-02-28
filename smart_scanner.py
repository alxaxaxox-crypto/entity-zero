# smart_scanner.py - ماسح ذكي يعمل مع Entity Zero
import time
import json
import os
import re
from datetime import datetime

# استيراد من المشروع
try:
    from config import *
    from entity_zero_bot import EntityZeroGUI, StatsManager
except ImportError:
    print("⚠️ تنبيه: ملفات config أو entity_zero_bot غير موجودة، سأستمر بالمهام الأساسية.")

class SmartScanner:
    def __init__(self):
        self.targets_file = "targets.txt"
        self.replied_file = "replied.json"
        self.replied = self._load_replied()

    def _load_replied(self):
        """تحميل قائمة الردود السابقة"""
        try:
            if os.path.exists(self.replied_file):
                with open(self.replied_file, 'r') as f:
                    return set(json.load(f))
        except Exception as e:
            print(f"⚠️ خطأ في تحميل الردود السابقة: {e}")
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

    def scan_and_reply(self, auto_reply=False, delay=60):
        """
        المسح والرد الذكي
        """
        targets = self._load_targets()
        if not targets:
            print("📭 ما في أهداف في targets.txt")
            return

        print(f"\n{'='*60}")
        print(f"🤖 Smart Scanner: {len(targets)} هدف")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎯 الوضع: {'تلقائي' if auto_reply else 'يدوي (معاينة)'}")
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

            if auto_reply:
                print("   🤖 سيرد تلقائياً...")
                self._save_replied(tweet_id)
            else:
                print("   👁️ وضع المعاينة (ما رديت)")

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
            print(f"✅ أضفت الهدف بنجاح: {url}")
        except Exception as e:
            print(f"❌ فشل إضافة الهدف: {e}")

if __name__ == "__main__":
    scanner = SmartScanner()
    scanner.scan_and_reply(auto_reply=False, delay=2)