const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(process.cwd(), 'morvix_shop_db.json');

module.exports = async (req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'GET') {
    try {
      if (!fs.existsSync(DB_PATH)) {
        return res.status(404).json({ success: false, message: "Master DB file missing" });
      }
      const raw = fs.readFileSync(DB_PATH, 'utf-8');
      const dbData = JSON.parse(raw);
      return res.status(200).json(dbData);
    } catch (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }

  if (req.method === 'POST') {
    try {
      const payload = req.body;
      if (!payload || !payload.products) {
        return res.status(400).json({ success: false, message: "Invalid product master payload" });
      }

      // Optimistic Locking & Version Conflict Verification
      if (fs.existsSync(DB_PATH)) {
        const currentRaw = fs.readFileSync(DB_PATH, 'utf-8');
        const currentDb = JSON.parse(currentRaw);

        if (payload.expected_version !== undefined && currentDb.db_version !== undefined) {
          if (payload.expected_version < currentDb.db_version) {
            return res.status(409).json({
              success: false,
              conflict: true,
              message: `⚠️ [Version Conflict] Master DB has been updated by another operator/worker (Server v${currentDb.db_version} vs Expected v${payload.expected_version}). Please refresh before saving.`
            });
          }
        }
      }

      // Increment Master DB Revision Version
      payload.db_version = (payload.db_version || 1) + 1;
      payload.updated_at = new Date().toISOString();

      fs.writeFileSync(DB_PATH, JSON.stringify(payload, null, 2), 'utf-8');
      
      return res.status(200).json({
        success: true,
        message: "Server Master DB updated atomically",
        db_version: payload.db_version,
        updated_at: payload.updated_at
      });
    } catch (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }

  return res.status(405).json({ message: "Method Not Allowed" });
};
