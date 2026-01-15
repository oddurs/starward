#!/usr/bin/env node

/**
 * Generate Open Graph social card image for starward documentation.
 *
 * Takes a screenshot of the homepage hero section with the animated
 * starfield background for beautiful social media previews.
 */

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const BUILD_DIR = path.join(__dirname, '..', 'build');
const OUTPUT_PATH = path.join(__dirname, '..', 'build', 'img', 'starward-social-card.png');
const PORT = 3456;

// OG image optimal dimensions
const WIDTH = 1200;
const HEIGHT = 630;

async function waitForServer(url, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return true;
    } catch {
      await new Promise(r => setTimeout(r, 200));
    }
  }
  throw new Error(`Server not ready at ${url}`);
}

async function generateOGImage() {
  // Verify build exists
  if (!fs.existsSync(BUILD_DIR)) {
    console.error('Build directory not found. Run "npm run build" first.');
    process.exit(1);
  }

  console.log('Starting local server...');

  // Start serve in the build directory
  const server = spawn('npx', ['serve', BUILD_DIR, '-l', PORT.toString(), '-s'], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false
  });

  try {
    const url = `http://localhost:${PORT}`;
    await waitForServer(url);
    console.log(`Server ready at ${url}`);

    console.log('Launching browser...');
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Set viewport to OG image dimensions
    await page.setViewport({ width: WIDTH, height: HEIGHT });

    console.log('Loading homepage...');
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);

    // Wait for Vanta.js animation to initialize and render beautifully
    // Using domcontentloaded + longer delay since networkidle0 never fires
    // due to continuous WebGL rendering
    console.log('Waiting for animation...');
    await new Promise(r => setTimeout(r, 5000));

    // Ensure output directory exists
    const outputDir = path.dirname(OUTPUT_PATH);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log('Capturing screenshot...');
    await page.screenshot({
      path: OUTPUT_PATH,
      type: 'png',
      clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT }
    });

    await browser.close();
    console.log(`OG image saved to: ${OUTPUT_PATH}`);

  } finally {
    // Clean up server - kill entire process tree
    server.kill('SIGKILL');
  }
}

generateOGImage()
  .then(() => process.exit(0))
  .catch(err => {
    console.error('Failed to generate OG image:', err);
    process.exit(1);
  });
