import sys, re, cairosvg, numpy as np, cv2
S='/tmp/claude-0/-home-claude/e73f4353-fe82-5241-899e-a18cfe95ce4f/scratchpad'; OUT='/home/claude/merch/studio/art'
sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
ARCH=FN+'archivo/files/archivo-latin-900-italic.woff2'
ACC={'green':'#39FF7A','red':'#D6001C'}
def save(name,d,w,h,extra=''):
    for cw,hx in ACC.items():
        sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.1f}mm" height="{h:.1f}mm" viewBox="0 0 {w:.1f} {h:.1f}"><path d="{d}" fill="{hx}"{extra}/></svg>'
        open(f'{OUT}/{name}_{cw}.svg','w').write(sv)
        cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=3000)
# back name: exactly the front wordmark recipe (Archivo 900 italic, size 100, TM at 38) -> 'bass™'
d,w=text_path('bass',ARCH,100,0,100); tm,tw=text_path('™',ARCH,38,w+4,52)
save('k4_bass',d+' '+tm,round(w+tw+8),128)
# number: same face, extra slant (skewX -14), solid, no outline
d,w=text_path('31',ARCH,300,0,300,tracking=0.03)
def ink_bbox(body,W,H):
    sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'
    im=cv2.imdecode(np.frombuffer(cairosvg.svg2png(bytestring=sv.encode()),np.uint8),cv2.IMREAD_UNCHANGED)[:,:,3]
    ys,xs=np.where(im>0); return xs.min(),xs.max(),ys.min(),ys.max()
def save_g(name,body,W,H,pad=2):
    x0,x1,y0,y1=ink_bbox(body.replace('FILL','#000'),W,H)
    w,h=x1-x0+2*pad,y1-y0+2*pad
    for cw,hx in ACC.items():
        sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w/4:.1f}mm" height="{h/4:.1f}mm" viewBox="{x0-pad} {y0-pad} {w} {h}">{body.replace("FILL",hx)}</svg>'
        open(f'{OUT}/{name}_{cw}.svg','w').write(sv)
        cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=3000)
d,w=text_path('31',ARCH,300,140,330,tracking=0.03)
save_g('k4_num31',f'<g transform="skewX(-13)"><path d="{d}" fill="FILL"/></g>',int(w+320),380)
# sleeve badge: ring of mono text around X monogram
MONO6=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2'
xm=open(S+'/el3/x_monogram_v2.svg').read(); vb,xb=inner(xm)
import math
R=100; parts=[f'<circle cx="120" cy="120" r="{R+12}" fill="none" stroke="FILL" stroke-width="5"/>',f'<circle cx="120" cy="120" r="{R-22}" fill="none" stroke="FILL" stroke-width="3"/>']
txt='REVERSED · KIT 01 · 160 BPM · '
n=len(txt)
for i,ch in enumerate(txt):
    if ch==' ': continue
    ang=-90+360*i/n
    dch,cw=text_path(ch,MONO6,22,0,0,anchor='middle')
    x=120+ (R-5)*math.cos(math.radians(ang)); y=120+(R-5)*math.sin(math.radians(ang))
    parts.append(f'<g transform="translate({x:.2f},{y:.2f}) rotate({ang+90:.2f}) translate(0,8)"><path d="{dch}" fill="FILL"/></g>')
xb2=re.sub(r'fill="[^"]*"','',xb)
parts.append(f'<svg x="78" y="83" width="84" height="74" viewBox="{vb}"><g fill="FILL">{xb2}</g></svg>')
save_g('k4_badge',''.join(parts),240,240)
print('ok')
