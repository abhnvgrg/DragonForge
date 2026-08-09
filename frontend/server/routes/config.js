import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

export default function configRoutes(configPath) {
  const router = (req, res, next) => {
    router.handle(req, res, next);
  };

  router.handle = (req, res, next) => {
    if (req.path === '/' || req.path === '') {
      // GET /api/config - return full config
      if (fs.existsSync(configPath)) {
        const content = fs.readFileSync(configPath, 'utf-8');
        const config = yaml.load(content);
        res.json(config);
      } else {
        res.status(404).json({ error: 'Config not found' });
      }
    } else if (req.path === '/model') {
      // GET /api/config/model - return model config for display
      if (fs.existsSync(configPath)) {
        const content = fs.readFileSync(configPath, 'utf-8');
        const config = yaml.load(content);
        res.json({
          bdh: config.model?.bdh,
          transformer: config.model?.transformer
        });
      } else {
        res.status(404).json({ error: 'Config not found' });
      }
    } else if (req.path === '/instrumentation') {
      // GET /api/config/instrumentation - return instrumentation config
      if (fs.existsSync(configPath)) {
        const content = fs.readFileSync(configPath, 'utf-8');
        const config = yaml.load(content);
        res.json(config.instrumentation);
      } else {
        res.status(404).json({ error: 'Config not found' });
      }
    } else {
      next();
    }
  };

  return router;
}