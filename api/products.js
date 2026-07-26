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
        return res.status(404).json({ success: false, message: "DB file missing" });
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
      
      fs.writeFileSync(DB_PATH, JSON.stringify(payload, null, 2), 'utf-8');
      return res.status(200).json({ success: true, message: "Server Product Master DB updated successfully", timestamp: new Date().toISOString() });
    } catch (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
  }

  return res.status(405).json({ message: "Method Not Allowed" });
};
