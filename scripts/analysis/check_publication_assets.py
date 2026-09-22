from pathlib import Path
from PIL import Image
import hashlib, numpy as np
root=Path(__file__).resolve().parents[2]
img=root/'tb/images/Tokinokane2005-1-4.jpg'; assert hashlib.sha256(img.read_bytes()).hexdigest()=='8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4'
paths=[root/'results/processed/arch-b/gate3-real-reference.png',root/'results/processed/arch-b/gate3-real-rtl.png',root/'results/processed/arch-b/gate3-real-diff.png',root/'results/processed/arch-b/arch-a-vs-b-diff.png']
for p in [img,*paths]:
 with Image.open(p) as im: assert im.size==(640,480), (p,im.size)
with Image.open(paths[2]) as im: assert np.asarray(im).max()==0
with Image.open(paths[3]) as im: assert np.asarray(im).max()==0
print('PUBLICATION_ASSETS=PASS')
