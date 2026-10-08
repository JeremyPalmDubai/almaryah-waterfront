"""Regenerate committed HTML from centralized data; Python is only needed by editors."""
from pathlib import Path
import subprocess, sys, shutil
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'content-source/build.py')],check=True)
for p in (root/'content-source/dist').rglob('*'):
 if not p.is_file() or p.name in ('_headers','_redirects'): continue
 target=(root if p.suffix=='.html' else root/'public')/p.relative_to(root/'content-source/dist')
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(p,target)
print('HTML and sitemaps updated. Run npm run build, then commit the changes.')
