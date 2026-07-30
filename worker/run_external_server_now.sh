#!/bin/bash
echo "=========================================================="
echo "🚀 MORVIX SHOP - External Server Autonomous Ingestion"
echo "=========================================================="
git config user.name "MORVIX External Server"
git config user.email "server@morvix.io"
python worker/sharelink_toss_harvester.py
git add morvix_shop_db.json
git diff --quiet && git diff --staged --quiet || (
    git commit -m "feat(external): Autonomous External Server Ingestion & Auto-Deploy"
    git push origin main
)
echo "=========================================================="
echo "✅ External Server Execution Completed & Pushed to GitHub/Vercel!"
echo "=========================================================="
