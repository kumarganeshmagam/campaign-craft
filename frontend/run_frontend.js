#!/usr/bin/env node
/**
 * Frontend startup script
 * Cleans up port 3000 and starts the Vite development server
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

function killPort(port) {
  return new Promise((resolve) => {
    const cmd = `netstat -ano | findstr :${port}`;
    exec(cmd, (error, stdout, stderr) => {
      if (error || !stdout.trim()) {
        console.log(`[INFO] Port ${port} is free`);
        resolve();
        return;
      }

      try {
        const parts = stdout.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        console.log(`[INFO] Found process ${pid} on port ${port}, killing it...`);
        
        exec(`taskkill /PID ${pid} /F`, (err) => {
          console.log(`[INFO] Port ${port} cleaned up`);
          setTimeout(resolve, 1000);
        });
      } catch (e) {
        console.log(`[WARN] Could not clean port ${port}: ${e.message}`);
        resolve();
      }
    });
  });
}

async function start() {
  try {
    console.log('[INFO] Cleaning up port 3000...');
    await killPort(3000);

    console.log('[OK] Starting frontend development server...');
    console.log('[INFO] Server will start on http://127.0.0.1:5173');
    
    const frontendDir = __dirname;
    const vite = spawn('npm', ['run', 'dev'], {
      cwd: frontendDir,
      stdio: 'inherit',
      shell: true
    });

    vite.on('error', (err) => {
      console.error('[ERROR] Failed to start frontend:', err);
      process.exit(1);
    });

    vite.on('exit', (code) => {
      console.log(`[INFO] Frontend server exited with code ${code}`);
      process.exit(code);
    });
  } catch (e) {
    console.error('[ERROR]', e.message);
    process.exit(1);
  }
}

start();
