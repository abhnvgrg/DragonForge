import fs from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import yaml from 'js-yaml';

class FileCache {
  constructor() {
    this.jsonCache = new Map(); // filePath -> { mtimeMs, data }
    this.yamlCache = new Map(); // filePath -> { mtimeMs, data }
  }

  /**
   * Invalidate cache for a specific file path or entire cache.
   */
  invalidate(filePath) {
    if (!filePath) {
      this.jsonCache.clear();
      this.yamlCache.clear();
      return;
    }
    const resolved = path.resolve(filePath);
    this.jsonCache.delete(resolved);
    this.yamlCache.delete(resolved);
  }

  /**
   * Safely read and parse a JSON file asynchronously with caching.
   * @param {string} filePath 
   * @returns {Promise<any|null>}
   */
  async readJson(filePath) {
    const resolved = path.resolve(filePath);
    try {
      if (!existsSync(resolved)) {
        this.jsonCache.delete(resolved);
        return null;
      }

      const stat = await fs.stat(resolved);
      const cached = this.jsonCache.get(resolved);

      if (cached && cached.mtimeMs === stat.mtimeMs) {
        return cached.data;
      }

      const content = await fs.readFile(resolved, 'utf-8');
      const data = JSON.parse(content);
      this.jsonCache.set(resolved, { mtimeMs: stat.mtimeMs, data });
      return data;
    } catch (err) {
      console.error(`[FileCache] Error reading JSON from ${resolved}:`, err.message);
      return null;
    }
  }

  /**
   * Safely read and parse a YAML file asynchronously with caching.
   * @param {string} filePath 
   * @returns {Promise<any|null>}
   */
  async readYaml(filePath) {
    const resolved = path.resolve(filePath);
    try {
      if (!existsSync(resolved)) {
        this.yamlCache.delete(resolved);
        return null;
      }

      const stat = await fs.stat(resolved);
      const cached = this.yamlCache.get(resolved);

      if (cached && cached.mtimeMs === stat.mtimeMs) {
        return cached.data;
      }

      const content = await fs.readFile(resolved, 'utf-8');
      const data = yaml.load(content);
      this.yamlCache.set(resolved, { mtimeMs: stat.mtimeMs, data });
      return data;
    } catch (err) {
      console.error(`[FileCache] Error reading YAML from ${resolved}:`, err.message);
      return null;
    }
  }

  /**
   * Read all JSON files in a directory that match an optional filter.
   * @param {string} dir 
   * @param {(filename: string) => boolean} filterFn 
   * @returns {Promise<any[]>}
   */
  async readJsonDir(dir, filterFn = (f) => f.endsWith('.json')) {
    const resolvedDir = path.resolve(dir);
    try {
      if (!existsSync(resolvedDir)) {
        return [];
      }

      const dirEntries = await fs.readdir(resolvedDir);
      const matchingFiles = dirEntries.filter(filterFn).sort();

      const results = await Promise.all(
        matchingFiles.map(file => this.readJson(path.join(resolvedDir, file)))
      );

      return results.filter(item => item !== null);
    } catch (err) {
      console.error(`[FileCache] Error reading directory ${resolvedDir}:`, err.message);
      return [];
    }
  }
}

export const fileCache = new FileCache();
export default fileCache;
