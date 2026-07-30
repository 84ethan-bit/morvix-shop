#!/bin/bash
echo "=========================================================="
echo "🚀 MORVIX SHOP - External Server 1-Minute Ingestion Trigger"
echo "=========================================================="
python worker/sharelink_toss_harvester.py
git add morvix_shop_db.json
git commit -m "feat(external): 1-Minute External Server Ingestion & Auto-Deploy"
git push origin main
echo "=========================================================="
echo "✅ External Server Execution Complete! Vercel will deploy in 10s."
echo "=========================================================="
