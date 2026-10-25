import sys, cairosvg
S='/tmp/claude-0/-home-claude/e73f4353-fe82-5241-899e-a18cfe95ce4f/scratchpad'; OUT='/home/claude/merch/studio/art'
sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
ARC=FN+'archivo/files/archivo-latin-900-italic.woff2'
MONO6=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2'
ACC={'green':'#39FF7A','red':'#D6001C'}
def save(name,d,w,h,wmm,pad=2):
    for cw,hx in ACC.items():
        sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w+2*pad:.1f}mm" height="{h+2*pad:.1f}mm" viewBox="{-pad} {-pad} {w+2*pad:.1f} {h+2*pad:.1f}"><path d="{d}" fill="{hx}"/></svg>'
        open(f'{OUT}/{name}_{cw}.svg','w').write(sv)
        cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4000,int(wmm/25.4*300)))
from fontTools.ttLib import TTFont
def bbox_text(txt,font,size,tracking):
    d,w=text_path(txt,font,size,0,size,tracking=tracking)
    # measure real ink bbox by rendering
    import cv2,numpy as np
    sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*1.3+40:.0f}" height="{size*1.6:.0f}" viewBox="-20 0 {w*1.3+40:.0f} {size*1.6:.0f}"><path d="{d}"/></svg>'
    im=cv2.imdecode(np.frombuffer(cairosvg.svg2png(bytestring=sv.encode()),np.uint8),cv2.IMREAD_UNCHANGED)[:,:,3]
    ys,xs=np.where(im>0); x0,x1,y0,y1=xs.min()-20,xs.max()-20,ys.min(),ys.max()
    d,_=text_path(txt,font,size,-x0,size-y0,tracking=tracking)
    return d,x1-x0,y1-y0
d,w,h=bbox_text('BASS',ARC,100,0.02); save('k2_bass',d,w,h,200)
d,w,h=bbox_text('31',ARC,300,-0.02); save('k2_num31',d,w,h,290)
d,w,h=bbox_text('reversed the bass  /  kit 01  /  160 bpm',MONO6,20,0.06); save('k2_backline',d,w,h,180)
print('ok')
