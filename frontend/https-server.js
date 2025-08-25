const https = require('https');
const fs = require('fs');
const path = require('path');
const express = require('express');

const app = express();

// Serve static files from build directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle React Router
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Create self-signed certificate for development
const selfsigned = require('selfsigned');
const attrs = [{ name: 'commonName', value: 'localhost' }];
const pems = selfsigned.generate(attrs, { days: 365 });

const options = {
  key: pems.private,
  cert: pems.cert
};

const server = https.createServer(options, app);

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`HTTPS Server running on https://localhost:${PORT}`);
  console.log('Voice recognition should now work!');
});
