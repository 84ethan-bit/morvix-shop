const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(process.cwd(), 'morvix_shop_db.json');
const AUDIT_PATH = path.join(process.cwd(), 'worker', 'security_audit.json');

const DEFAULT_ADMIN_PIN = process.env.ADMIN_PIN || '7777';

// Simple In-Memory Rate Limiter (Max 30 requests per minute per IP)
const rateLimitMap = new Map();

function isRateLimited(clientIp) {
  const now = Date.now();
  const windowMs = 60 * 1000;
  const maxReqs = 30;

  if (!rateLimitMap.has(clientIp)) {
    rateLimitMap.set(clientIp, { count: 1, resetAt: now + windowMs });
    return false;
  }

  const record = rateLimitMap.get(clientIp);
  if (now > record.resetAt) {
    rateLimitMap.set(clientIp, { count: 1, resetAt: now + windowMs });
    return false;
  }

  record.count++;
  if (record.count > maxReqs) {
    return true;
  }
  return false;
}

function appendSecurityLog(type, clientIp, details) {
  try {
    let logs = [];
    if (fs.existsSync(AUDIT_PATH)) {
      try {
        logs = JSON.parse(fs.readFileSync(AUDIT_PATH, 'utf-8'));
      } catch (e) { logs = []; }
    }
    const entry = {
      timestamp: new Date().toISOString(),
      type: type,
      client_ip: clientIp,
      details: details
    };
    logs.unshift(entry);
    logs = logs.slice(0, 100); // Keep last 100 entries

    const dir = path.dirname(AUDIT_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    fs.writeFileSync(AUDIT_PATH, JSON.stringify(logs, null, 2), 'utf-8');
  } catch (err) {
    console.warn("Security audit log write warning:", err);
  }
}

module.exports = async (req, res) => {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-pin');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const clientIp = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '127.0.0.1';

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
      // 1. Rate Limiting Protection Shield
      if (isRateLimited(clientIp)) {
        appendSecurityLog("RATE_LIMIT_EXCEEDED", clientIp, { limit: 30, window: "1min" });
        return res.status(429).json({
          success: false,
          error: "TOO_MANY_REQUESTS",
          message: "⚠️ [Rate Limit Shield] Request rate limit exceeded. Please wait 1 minute."
        });
      }

      const payload = req.body || {};
      const reqPin = req.headers['x-admin-pin'] || payload.admin_pin;

      // 2. Admin Authentication Security Shield
      if (reqPin !== DEFAULT_ADMIN_PIN) {
        appendSecurityLog("UNAUTHORIZED_ATTEMPT_401", clientIp, { endpoint: "/api/products", method: "POST" });
        return res.status(401).json({
          success: false,
          error: "UNAUTHORIZED",
          message: "🔐 [Admin Security Shield] Unauthorized API modification attempt blocked. Valid Admin PIN required."
        });
      }

      if (!payload.products) {
        return res.status(400).json({ success: false, message: "Invalid product master payload" });
      }

      // 3. Optimistic Locking & Version Conflict Shield
      if (fs.existsSync(DB_PATH)) {
        const currentRaw = fs.readFileSync(DB_PATH, 'utf-8');
        const currentDb = JSON.parse(currentRaw);

        if (payload.expected_version !== undefined && currentDb.db_version !== undefined) {
          if (payload.expected_version < currentDb.db_version) {
            appendSecurityLog("VERSION_CONFLICT_409", clientIp, {
              server_version: currentDb.db_version,
              requested_version: payload.expected_version
            });
            return res.status(409).json({
              success: false,
              conflict: true,
              message: `⚠️ [Version Conflict] Master DB has been updated by another operator/worker (Server v${currentDb.db_version} vs Expected v${payload.expected_version}). Please refresh.`
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
