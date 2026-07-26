const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const DIST_DIR = path.join(ROOT_DIR, 'dist');

console.log("=======================================================");
console.log("📦 MORVIX SHOP OS Static Build Engine Running...");
console.log("=======================================================\n");

// Ensure clean dist directory
if (fs.existsSync(DIST_DIR)) {
  fs.rmSync(DIST_DIR, { recursive: true, force: true });
}
fs.mkdirSync(DIST_DIR, { recursive: true });

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    for (const item of fs.readdirSync(src)) {
      copyRecursive(path.join(src, item), path.join(dest, item));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

const FILES_TO_COPY = [
  "index.html",
  "styles.css",
  "app.js",
  "morvix_shop_db.json",
  "favicon.svg",
  "sitemap.xml",
  "robots.txt",
  "release.json"
];

for (const file of FILES_TO_COPY) {
  const srcPath = path.join(ROOT_DIR, file);
  const destPath = path.join(DIST_DIR, file);
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    printLog(`Copied file: ${file}`);
  }
}

const DIRS_TO_COPY = ["images", "public"];
for (const dir of DIRS_TO_COPY) {
  const srcDir = path.join(ROOT_DIR, dir);
  const destDir = path.join(DIST_DIR, dir);
  if (fs.existsSync(srcDir)) {
    copyRecursive(srcDir, destDir);
    printLog(`Copied directory: ${dir}/`);
  }
}

function printLog(msg) {
  console.log(`  ✅ ${msg}`);
}

console.log("\n=======================================================");
console.log("🎉 Static Bundle Successfully Generated in /dist/");
console.log("=======================================================");
