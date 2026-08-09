import fs from 'fs';
import path from 'path';

export default function summaryRoutes(resultsDir) {
  const router = (req, res, next) => {
    router.handle(req, res, next);
  };

  router.handle = (req, res, next) => {
    const summaryPath = path.join(resultsDir, 'summary.json');
    
    if (req.path === '/' || req.path === '') {
      // GET /api/summary - return summary
      if (fs.existsSync(summaryPath)) {
        const content = fs.readFileSync(summaryPath, 'utf-8');
        res.json(JSON.parse(content));
      } else {
        res.status(404).json({ error: 'Summary not found' });
      }
    } else if (req.path === '/headline') {
      // GET /api/summary/headline - return just the headline
      if (fs.existsSync(summaryPath)) {
        const content = fs.readFileSync(summaryPath, 'utf-8');
        const data = JSON.parse(content);
        res.json({ headline: data.headline });
      } else {
        res.status(404).json({ error: 'Summary not found' });
      }
    } else {
      next();
    }
  };

  return router;
}