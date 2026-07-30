import os
import sys
import json
import re
import datetime

# Set UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'morvix_shop_db.json')

def parse_discount_num(val):
    if not val: return 0
    nums = re.sub(r'[^\d]', '', str(val))
    return int(nums) if nums else 0

def run_midnight_rotation():
    print("==========================================================")
    print("🌙 MORVIX Midnight 00:10 KST Time Attack Rotation Triggered")
    print(f"⏰ Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================================================")

    if not os.path.exists(DB_PATH):
        print(f"❌ DB file not found at {DB_PATH}")
        return

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    products = db.get('products', [])

    # Step 1: Purge / Expire old timeattack deals below 35% discount
    purged_count = 0
    for p in products:
        d_val = parse_discount_num(p.get('discount_rate'))
        if p.get('is_featured') and d_val < 35:
            p['is_featured'] = False
            purged_count += 1

    print(f"🧹 Step 1: Successfully purged {purged_count} expired/low-discount time attack deals.")

    # Step 2: Select Top 3 highest discount deals for 00:10 KST Time Attack Lineup
    active_deals = [p for p in products if p.get('status') == 'ACTIVE' and p.get('thumbnail')]
    sorted_by_discount = sorted(active_deals, key=lambda x: parse_discount_num(x.get('discount_rate')), reverse=True)

    for i, p in enumerate(sorted_by_discount):
        if i < 3:
            p['is_featured'] = True
            p['expiry_date'] = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        else:
            p['is_featured'] = False

    print(f"✨ Step 2: Selected Top 3 fresh high-discount deals for 00:10 KST Time Attack lineup.")

    # Step 3: Save DB
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("✅ Step 3: Saved updated morvix_shop_db.json successfully.")
    print("==========================================================")

if __name__ == '__main__':
    run_midnight_rotation()
