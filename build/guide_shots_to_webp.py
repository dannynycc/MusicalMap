# shots/*.png → assets/guide/{hl}/{name}.webp;wall/stats 裁上緣;印出各檔尺寸
import io, os, sys
from PIL import Image
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = r'C:\Users\Home\AppData\Local\Temp\claude\C--Users-Home\79bfe7d5-ce91-4131-96a1-9968e0d0425f\scratchpad\shots'
DST = r'D:\ClaudeCode\MusicalMap\assets\guide'
CROP_H = {'wall': 1080, 'stats': 1320}   # 2x px;其餘不裁
for hl in ['zh-hant', 'zh-hans', 'en']:
    os.makedirs(os.path.join(DST, hl), exist_ok=True)
    for name in ['map', 'popup', 'form', 'stats', 'wall']:
        p = os.path.join(SRC, f'{name}_{hl}.png')
        im = Image.open(p).convert('RGB')
        if name in CROP_H and im.height > CROP_H[name]:
            im = im.crop((0, 0, im.width, CROP_H[name]))
        out = os.path.join(DST, hl, f'{name}.webp')
        im.save(out, 'WEBP', quality=82, method=6)
        print(hl, name, im.size, f'{os.path.getsize(out)//1024}KB')
