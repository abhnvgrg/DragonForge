import fs from 'fs';
import path from 'path';

function readJsonFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  
  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.json'))
    .sort();
  
  return files.map(file => {
    const content = fs.readFileSync(path.join(dir, file), 'utf-8');
    return JSON.parse(content);
  });
}

function getLatestCheckpoint(dir) {
  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.json') && f.startsWith('checkpoint_'))
    .sort();
  
  if (files.length === 0) return null;
  
  const latest = files[files.length - 1];
  const content = fs.readFileSync(path.join(dir, latest), 'utf-8');
  return JSON.parse(content);
}

function getAllCheckpoints(dir) {
  if (!fs.existsSync(dir)) return [];
  
  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.json') && f.startsWith('checkpoint_'))
    .sort();
  
  return files.map(file => {
    const content = fs.readFileSync(path.join(dir, file), 'utf-8');
    return JSON.parse(content);
  });
}

export default function structureRoutes(resultsDir) {
  const router = (req, res, next) => {
    router.handle(req, res, next);
  };

  router.handle = (req, res, next) => {
    const structureDir = path.join(resultsDir, 'structure');
    
    if (req.path === '/' || req.path === '') {
      // GET /api/structure - return all checkpoints
      const checkpoints = getAllCheckpoints(structureDir);
      res.json({ checkpoints, count: checkpoints.length });
    } else if (req.path === '/latest') {
      // GET /api/structure/latest - return latest checkpoint
      const latest = getLatestCheckpoint(structureDir);
      if (latest) {
        res.json(latest);
      } else {
        res.status(404).json({ error: 'No checkpoint data found' });
      }
    } else if (req.path === '/comparison') {
      // GET /api/structure/comparison - return BDH vs Transformer comparison
      const bdhDir = path.join(structureDir, 'bdh');
      const transDir = path.join(structureDir, 'transformer');
      
      const bdhMetrics = fs.existsSync(path.join(bdhDir, 'bdh_structural_metrics.json'))
        ? JSON.parse(fs.readFileSync(path.join(bdhDir, 'bdh_structural_metrics.json'), 'utf-8'))
        : null;
      
      const transMetrics = fs.existsSync(path.join(transDir, 'transformer_structural_metrics.json'))
        ? JSON.parse(fs.readFileSync(path.join(transDir, 'transformer_structural_metrics.json'), 'utf-8'))
        : null;
      
      res.json({ bdh: bdhMetrics, transformer: transMetrics });
    } else if (req.path === '/graph') {
      // GET /api/structure/graph - return graph data for visualization
      const model = req.query.model || 'bdh';
      const graphPath = path.join(structureDir, model, `${model}_interaction_graph.json`);
      
      if (fs.existsSync(graphPath)) {
        const content = fs.readFileSync(graphPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        res.status(404).json({ error: `Graph data not found for ${model}` });
      }
    } else {
      next();
    }
  };

  return router;
}