import fs from 'fs';
import path from 'path';

export default function reasoningRoutes(resultsDir) {
  const router = (req, res, next) => {
    router.handle(req, res, next);
  };

  router.handle = (req, res, next) => {
    const reasoningDir = path.join(resultsDir, 'reasoning');
    const resultPath = path.join(reasoningDir, 'result.json');
    
    if (req.path === '/' || req.path === '') {
      // GET /api/reasoning - return long-context reasoning results
      if (fs.existsSync(resultPath)) {
        const content = fs.readFileSync(resultPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        res.status(404).json({ error: 'Long-context reasoning results not found' });
      }
    } else if (req.path === '/comparison') {
      // GET /api/reasoning/comparison - return formatted comparison table
      if (fs.existsSync(resultPath)) {
        const content = fs.readFileSync(resultPath, 'utf-8');
        const data = JSON.parse(content);
        
        // Format for comparison table
        const comparison = {
          tasks: Object.keys(data.accuracies || {}).map(task => ({
            name: task,
            bdh: {
              mean: data.bdh_accuracy_mean,
              std: data.bdh_accuracy_std
            },
            transformer: {
              mean: data.transformer_accuracy_mean,
              std: data.transformer_accuracy_std
            },
            seeds: data.seeds,
            tag: data.tag
          }))
        };
        
        res.json(comparison);
      } else {
        res.status(404).json({ error: 'Reasoning results not found' });
      }
    } else {
      next();
    }
  };

  return router;
}