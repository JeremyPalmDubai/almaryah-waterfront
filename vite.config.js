import { defineConfig } from 'vite';
import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';
const root = import.meta.dirname;
function pages(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    if (['node_modules', 'dist', 'public', '.git', 'content-source'].includes(entry.name)) return [];
    const path = resolve(dir, entry.name);
    return entry.isDirectory() ? pages(path) : entry.name.endsWith('.html') ? [path] : [];
  });
}
export default defineConfig({
  appType: 'mpa',
  publicDir: 'public',
  build: { outDir: 'dist', emptyOutDir: true, rolldownOptions: { input: pages(root) } }
});
