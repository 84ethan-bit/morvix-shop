/* ==========================================================================
   MORVIX SHOP OS v7.2 - Concurrent Save & Security Shield Test Suite
   ========================================================================== */

const fs = require('fs');
const path = require('path');
const apiHandler = require('./api/products.js');

const DB_PATH = path.join(__dirname, 'morvix_shop_db.json');

// Mock Express/Vercel Req/Res helper
function createMockReqRes(method, headers = {}, body = {}) {
  return new Promise((resolve) => {
    const req = { method, headers, body };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) { this.headers[k] = v; },
      status(code) { this.statusCode = code; return this; },
      json(payload) {
        resolve({ statusCode: this.statusCode, payload });
      },
      end() {
        resolve({ statusCode: this.statusCode, payload: {} });
      }
    };
    apiHandler(req, res);
  });
}

async function runConcurrentLockTests() {
  console.log("=======================================================");
  console.log("🛡️ Starting MORVIX SHOP OS Concurrent Lock & Auth Security Test Suite...");
  console.log("=======================================================\n");

  const raw = fs.readFileSync(DB_PATH, 'utf-8');
  const dbData = JSON.parse(raw);
  const currentVersion = dbData.db_version || 5;

  console.log(`[TEST 1] Unauthorized Write Attempt Protection Test...`);
  const unauthRes = await createMockReqRes('POST', {}, { products: dbData.products });
  if (unauthRes.statusCode === 401) {
    console.log(`✅ [PASS] Unauthorized write attempt blocked cleanly (HTTP 401 Unauthorized)`);
  } else {
    console.log(`❌ [FAIL] Unauthorized write protection failed. Status: ${unauthRes.statusCode}`);
  }

  console.log(`\n[TEST 2] Authorized Write Test (Valid Admin PIN: 7777)...`);
  const authRes = await createMockReqRes('POST', { 'x-admin-pin': '7777' }, { products: dbData.products, db_version: currentVersion, expected_version: currentVersion });
  if (authRes.statusCode === 200) {
    console.log(`✅ [PASS] Authorized write completed (HTTP 200 OK, New DB Version: v${authRes.payload.db_version})`);
  } else {
    console.log(`❌ [FAIL] Authorized write failed. Status: ${authRes.statusCode}`);
  }

  console.log(`\n[TEST 3] Out-of-Date Version Conflict Protection Shield Test...`);
  const staleVersion = currentVersion - 1; // Out-of-date version
  const conflictRes = await createMockReqRes('POST', { 'x-admin-pin': '7777' }, { products: dbData.products, db_version: staleVersion, expected_version: staleVersion });
  if (conflictRes.statusCode === 409) {
    console.log(`✅ [PASS] Out-of-date version conflict blocked cleanly (HTTP 409 Conflict Shield)`);
    console.log(`   Message: "${conflictRes.payload.message}"`);
  } else {
    console.log(`❌ [FAIL] Version conflict shield failed. Status: ${conflictRes.statusCode}`);
  }

  console.log("\n=======================================================");
  console.log("📊 ALL SECURITY & CONCURRENT LOCK TESTS COMPLETED 100%!");
  console.log("=======================================================");
}

runConcurrentLockTests();
