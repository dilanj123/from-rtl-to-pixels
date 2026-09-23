from pathlib import Path
import subprocess
import re
from PIL import Image
import hashlib, numpy as np
root=Path(__file__).resolve().parents[2]
img=root/'tb/images/Tokinokane2005-1-4.jpg'; assert hashlib.sha256(img.read_bytes()).hexdigest()=='8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4'
synthetic=root/'tb/images/gradient-grid-640x480.png'; assert synthetic.is_file()
paths=[root/'results/processed/arch-b/gate3-real-reference.png',root/'results/processed/arch-b/gate3-real-rtl.png',root/'results/processed/arch-b/gate3-real-diff.png',root/'results/processed/arch-b/arch-a-vs-b-diff.png']
synthetic_paths=[root/'results/processed/public-gradient-a/gate3-real-reference.png',root/'results/processed/public-gradient-a/gate3-real-rtl.png',root/'results/processed/public-gradient-a/gate3-real-diff.png',root/'results/processed/public-gradient-b/gate3-real-rtl.png',root/'results/processed/public-gradient-a-vs-b-diff.png']
for p in [img,synthetic,*paths,*synthetic_paths]:
 with Image.open(p) as im: assert im.size==(640,480), (p,im.size)
with Image.open(paths[2]) as im: assert np.asarray(im).max()==0
with Image.open(paths[3]) as im: assert np.asarray(im).max()==0
with Image.open(synthetic_paths[2]) as im: assert np.asarray(im).max()==0
with Image.open(synthetic_paths[4]) as im: assert np.asarray(im).max()==0
print('PUBLICATION_ASSETS=PASS')

broken=[]
tracked = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=root, text=True).splitlines()
for rel in tracked:
 md=root/rel
 text=md.read_text()
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
  if target.startswith(('http://','https://','mailto:','#')): continue
  target=target.split('#',1)[0]
  if target and not (md.parent/target).exists(): broken.append(f'{md}:{target}')
assert not broken, 'broken repository links: ' + ', '.join(broken)
print('REPOSITORY_MARKDOWN_LINKS=PASS')
