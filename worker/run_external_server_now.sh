#!/bin/bash
echo "=========================================================="
echo "🚀 MORVIX SHOP - External Server Instant Ingestion Trigger"
echo "=========================================================="
python worker/sharelink_toss_harvester.py
git add morvix_shop_db.json
git commit -m "feat(external): External Server Instant Ingestion & Auto-Deploy"
git push origin main
echo "=========================================================="
echo "✅ External Server Execution Complete! Vercel will deploy in 10s."
echo "=========================================================="
