import sys, os, subprocess, html
from PIL import Image, ImageChops
src, out, work = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith('.mmd'): continue
    code = open(os.path.join(src, f)).read()
    page = os.path.join(work, f + '.html')
    open(page, 'w').write(f"""<!doctype html><html><head><meta charset="utf-8">
<style>body{{margin:0;background:#fff}} #d{{display:inline-block;padding:16px}}</style>
<script src="mermaid.min.js"></script></head><body><div id="d"><pre class="mermaid">{html.escape(code)}</pre></div>
<script>mermaid.initialize({{startOnLoad:true,theme:'neutral',fontFamily:'Arial, sans-serif',flowchart:{{useMaxWidth:false}},sequence:{{useMaxWidth:false}},state:{{useMaxWidth:false}}}});</script>
</body></html>""")
    png = os.path.join(out, f[:-4] + '.png')
    subprocess.run(['chromium','--headless','--no-sandbox','--disable-gpu','--hide-scrollbars',
        '--force-device-scale-factor=2','--window-size=3200,2600','--virtual-time-budget=8000',
        '--screenshot='+png, 'file://'+page], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    im = Image.open(png).convert('RGB')
    bbox = ImageChops.difference(im, Image.new('RGB', im.size, (255,255,255))).getbbox()
    if bbox:
        im = im.crop((max(0,bbox[0]-20), max(0,bbox[1]-20), min(im.width,bbox[2]+20), min(im.height,bbox[3]+20)))
    im.save(png)
    print(f, im.size, 'EMPTY' if not bbox else '')
