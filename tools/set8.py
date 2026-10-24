# KIT 01 — clean jersey graphics (cm-space SVG -> PNG)
import sys, re, cairosvg
S='/tmp/claude-0/-home-claude/e73f4353-fe82-5241-899e-a18cfe95ce4f/scratchpad'; OUT='/home/claude/merch/studio/art'
sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'
COND=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-800-normal.woff2'
K='#000000'
ACC={'green':'#39FF7A','red':'#D6001C'}
def doc(w,h,b,defs=''): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{b}</svg>'
def save(name,svg,wmm,maps,dpi=300):
    for cw,hx in maps.items():
        cs=svg.replace(K,hx); open(f'{OUT}/{name}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4000,int(wmm/25.4*dpi)))

# 1. number 31 — solid with a detached keyline (one ink), raster->trace
import numpy as np, cv2, io
from vec import trace_mask
def rast(svgtxt,wpx):
    png=cairosvg.svg2png(bytestring=svgtxt.encode(),output_width=wpx)
    im=cv2.imdecode(np.frombuffer(png,np.uint8),cv2.IMREAD_UNCHANGED); return im[:,:,3]>127
def save_mask(name,m,wmm,maps,pxmm):
    h,w=m.shape; pl=potrace_svg(m)
    for cw,hx in maps.items():
        sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w/pxmm:.1f}mm" height="{h/pxmm:.1f}mm" viewBox="0 0 {w} {h}"><path d="{pl}" fill="{hx}" fill-rule="evenodd"/></svg>'
        open(f'{OUT}/{name}_{cw}.svg','w').write(sv)
        cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4000,int(w/pxmm/25.4*300)))
def potrace_svg(m):
    import potrace
    pl=potrace.Bitmap(~m).trace(turdsize=20,alphamax=1.0,opticurve=True,opttolerance=0.2); parts=[]
    for c in pl:
        st=c.start_point; seg=[f"M{st.x:.1f} {st.y:.1f}"]
        for sg in c.segments:
            if sg.is_corner: seg.append(f"L{sg.c.x:.1f} {sg.c.y:.1f} L{sg.end_point.x:.1f} {sg.end_point.y:.1f}")
            else: seg.append(f"C{sg.c1.x:.1f} {sg.c1.y:.1f} {sg.c2.x:.1f} {sg.c2.y:.1f} {sg.end_point.x:.1f} {sg.end_point.y:.1f}")
        parts.append(" ".join(seg)+"Z")
    return " ".join(parts)
d,w=text_path('31',COND9,300,40,270,tracking=0.10)
W,H=round(w)+80,310; PX=8  # px per mm
num=rast(doc(W,H,f'<path d="{d}" fill="{K}"/>'),W*PX)
def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
gap=cv2.dilate(num.astype(np.uint8),disk(int(7*PX)))>0
out=cv2.dilate(num.astype(np.uint8),disk(int(13*PX)))>0
m=num|(out&~gap)
save_mask('k_num31',m,W,ACC,PX)
# 2. BASS nameplate, wide tracking
d,w=text_path('BASS',COND,100,0,80,tracking=0.16)
save('k_bass',doc(round(w)+2,84,f'<path d="{d}" fill="{K}"/>'),190,ACC)

# 3. chest bar with knocked-out wordmark (1000 x 70 mm), back bar with knocked-out BASS
wm=open(OUT+'/wm_reversed.svg').read(); vb,wb=inner(wm)
_,_,vw,vh=map(float,vb.split()); ww=230; wh=ww*vh/vw
BW,BH=1000,70; PX=4
wx=(BW-ww)/2; wy=(BH-wh)/2+4
t1=rast(doc(BW,BH,f'<svg x="{wx}" y="{wy}" width="{ww}" height="{wh}" viewBox="{vb}">{wb}</svg>'),BW*PX)
bar=np.ones_like(t1); save_mask('k_chestbar',bar&~t1,BW,ACC,PX)
d,w=text_path('BASS',COND,44,(BW)/2,BH/2+15.5,anchor='middle',tracking=0.24)
t2=rast(doc(BW,BH,f'<path d="{d}" fill="{K}"/>'),BW*PX)
save_mask('k_backbar',bar&~t2,BW,ACC,PX)
# 4. small dot-matrix hem tag  "KIT 01"
dd,w=dots('KIT 01',2.2,0,0)
save('k_kit01',doc(round(w)+1,16,f'<g fill="{K}">{dd}</g>'),40,ACC)
print('ok')
