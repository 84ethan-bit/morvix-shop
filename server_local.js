const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  let reqUrl = req.url.split('?')[0];

  // Short URL slug redirect (e.g. /fan001 -> index.html#fan001)
  if (reqUrl !== '/' && !reqUrl.includes('.')) {
    const slug = reqUrl.replace('/', '');
    res.writeHead(302, { 'Location': `/#${slug}` });
    return res.end();
  }

  let filePath = path.join(PUBLIC_DIR, reqUrl === '/' ? 'index.html' : reqUrl);
  let ext = path.extname(filePath);
  let contentType = MIME_TYPES[ext] || 'text/plain';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end('<h1>404 Not Found - MORVIX SHOP OS</h1>');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`🚀 MORVIX SHOP OS v1.0.0 Local Server Running Live!`);
  console.log(`👉 Main Shop Hub:  http://localhost:${PORT}/`);
  console.log(`👉 Short Slug Demo: http://localhost:${PORT}/fan001`);
  console.log(`=======================================================`);
});
