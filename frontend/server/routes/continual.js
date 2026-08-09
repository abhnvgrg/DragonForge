import fs from 'fs';
import path from 'path';

export default function continualRoutes(resultsDir) {
  const router = (req, res, next) => {
    router.handle(req, res, next);
  };

  router.handle = (req, res, next) => {
    const continualDir = path.join(resultsDir, 'continual');
    const resultPath = path.join(continualDir, 'result.json');
    
    if (req.path === '/' || req.path === '') {
      // GET /api/continual - return continual learning results
      if (fs.existsSync(resultPath)) {
        const content = fs.readFileSync(resultPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        res.status(404).json({ error: 'Continual learning results not found' });
      }
    } else if (req.path === '/bdh') {
      // GET /api/continual/bdh - return BDH-specific results
      const bdhPath = path.join(continualDir, 'bdh_result.json');
      if (fs.existsSync(bdhPath)) {
        const content = fs.readFileSync(bdhPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        // Try to extract from combined result
        if (fs.existsSync(resultPath)) {
          const content = fs.readFileSync(resultPath, 'utf-8');
          const data = JSON.parse(content);
          // Return BDH specific fields
          res.json({
            task_a_before: data.task_a_before,
            task_a_after: data.task_a_after,
            task_b_after: data.task_b_after,
            forgetting: data.forgetting,
            tag: data.tag,
            seeds: data.seeds
          });
        } else {
          res.status(404).json({ error: 'BDH continual results not found' });
        }
      }
    } else if (req.path === '/transformer') {
      // GET /api/continual/transformer - return Transformer baseline results
      const transPath = path.join(continualDir, 'transformer_result.json');
      if (fs.existsSync(transPath)) {
        const content = fs.readFileSync(transPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        if (fs.existsSync(resultPath)) {
          const content = fs.readFileSync(resultPath, 'utf-8');
          const data = JSON.parse(content);
          res.json(data.baseline_transformer || {});
        } else {
          res.status(404).json({ error: 'Transformer continual results not found' });
        }
      }
    } else {
      next();
    }
  };

  return router;
}