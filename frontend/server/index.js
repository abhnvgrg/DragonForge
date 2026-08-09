import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import chokidar from 'chokidar';

import structureRoutes from './routes/structure.js';
import continualRoutes from './routes/continual.js';
import reasoningRoutes from './routes/reasoning.js';
import summaryRoutes from './routes/summary.js';
import configRoutes from './routes/config.js';

const app = express();
const PORT = process.env.PORT || 3001;
const RESULTS_DIR = path.resolve('../../results');
const CONFIG_PATH = path.resolve('../../configs/default.yaml');

app.use(cors());
app.use(express.json());

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/structure', structureRoutes(RESULTS_DIR));
app.use('/api/continual', continualRoutes(RESULTS_DIR));
app.use('/api/reasoning', reasoningRoutes(RESULTS_DIR));
app.use('/api/summary', summaryRoutes(RESULTS_DIR));
app.use('/api/config', configRoutes(CONFIG_PATH));

// Global error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error', message: err.message });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

const server = app.listen(PORT, () => {
  console.log(`DragonForge API server running on http://localhost:${PORT}`);
  console.log(`Reading results from: ${RESULTS_DIR}`);
});

// Optional: Watch for file changes and log
const watcher = chokidar.watch(RESULTS_DIR, { ignored: /^\./, persistent: true });
watcher.on('change', (filePath) => {
  console.log(`[File changed] ${filePath}`);
});

export default app;