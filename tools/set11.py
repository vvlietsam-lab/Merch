import sys, cairosvg, numpy as np, cv2
S='/tmp/claude-0/-home-claude/e73f4353-fe82-5241-899e-a18cfe95ce4f/scratchpad'; OUT='/home/claude/merch/studio/art'
sys.path.insert(0,S+'/scripts')
from typo import *
exec('\n'.join(open(S+'/scripts/set8.py').read().split('# 1. number 31')[1].split('\n')[1:]).split("d,w=text_path('31'")[0])  # rast, save_mask, potrace_svg
FN=S+'/npm/node_modules/@fontsource/'
ARC=FN+'archivo/files/archivo-latin-900-italic.woff2'
ACC={'green':'#39FF7A','red':'#D6001C'}
def doc(w,h,b): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{b}</svg>'
def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
def crop(m,pad):
    ys,xs=np.where(m); return m[max(0,ys.min()-pad):ys.max()+pad, max(0,xs.min()-pad):xs.max()+pad]
PX=6
# layered block number: solid fill, thin knock-out line just outside the glyph, solid outer border
d,w=text_path('31',ARC,300,60,300,tracking=0.06)
W,H=int(w)+140,380
M=rast(doc(W,H,f'<path d="{d}"/>'),W*PX).astype(np.uint8)
ko=(cv2.dilate(M,disk(int(3.6*PX)))>0)&~(M>0)
outer=cv2.dilate(M,disk(int(10*PX)))>0
ink=crop(outer&~ko,4)
save_mask('k3_num31',ink,0,ACC,PX)
# lowercase 'bass' in the wordmark face
d,w=text_path('bass',ARC,100,20,110,tracking=-0.01)
B=rast(doc(int(w)+60,140,f'<path d="{d}"/>'),(int(w)+60)*PX)
save_mask('k3_bass',crop(B,4),0,ACC,PX)
print('ok')
