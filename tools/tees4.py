import sys, os, cv2, numpy as np, cairosvg
S=sys.argv[1]; A=sys.argv[2]; OUT=sys.argv[3]; sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
ARCH=FN+'archivo/files/archivo-latin-900-italic.woff2'; COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'; MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
K='#000000'
def doc(w,h,b): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{b}</svg>'
# desrever wordmark
d,w=text_path('desrever',ARCH,100,0,100); tm,tw=text_path('™',ARCH,38,w+4,52)
sv=doc(round(w+tw+8),128,f'<path d="{d} {tm}" fill="{K}"/>')
for cw,hx in {'green':'#39FF7A','red':'#D6001C'}.items():
    cs=sv.replace(K,hx); open(f'{OUT}/wm_desrever_{cw}.svg','w').write(cs); cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/wm_desrever_{cw}.png',output_width=2834)
# rave theme back print: text top + coloured halftone crowd + text bottom, DTF full colour
g=cv2.imread(f'{A}/7abe0b94-image.png',0).astype(np.float32)
g=cv2.resize(g,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC); H,W=g.shape
yy,xx=np.mgrid[0:H,0:W]; fy=np.clip(np.minimum(yy/(H*0.22),(H-yy)/(H*0.10)),0,1); fx=np.clip(np.minimum(xx,W-xx)/(W*0.06),0,1)
ramp=np.minimum(fy,fx)**0.8
ink=g<(255*0.5*ramp)
stops=[(0,(255,45,149)),(0.35,(255,138,0)),(0.65,(57,255,122)),(1,(47,212,255))]
def grad(t):
    for (a,ca),(b,cb) in zip(stops,stops[1:]):
        if t<=b: k=(t-a)/(b-a); return [ca[i]+(cb[i]-ca[i])*k for i in range(3)]
    return stops[-1][1]
cols=np.array([grad(t) for t in np.linspace(0,1,H)],np.float32)  # vertical gradient, slight diagonal
img=np.zeros((H,W,4),np.uint8)
diag=np.clip((yy/H)*0.8+(xx/W)*0.2,0,1); idx=(diag*(H-1)).astype(int)
img[...,0]=cols[idx,0]; img[...,1]=cols[idx,1]; img[...,2]=cols[idx,2]; img[...,3]=ink*255
from PIL import Image
crowd=Image.fromarray(img,'RGBA')
for cw,txt in {'black':(244,244,242),'white':(21,21,21)}.items():
    Wd=3780; pad=0
    top_svg=None
    d1,w1=text_path('RAVE OF THE YOUNG',COND9,100,0,82,tracking=0.04)
    t1=doc(round(w1)+2,90,f'<path d="{d1}" fill="rgb{txt}"/>')
    d2,w2=text_path('reversed',ARCH,100,0,100); tm,tw=text_path('™',ARCH,38,w2+4,52)
    t2=doc(round(w2+tw+8),128,f'<path d="{d2} {tm}" fill="rgb{txt}"/>')
    d3,w3=text_path('FOR THE ROOMS NOBODY LEAVES — 155/160',MONO,10,0,10,tracking=0.12)
    t3=doc(round(w3)+2,14,f'<path d="{d3}" fill="rgb{txt}"/>')
    import io
    def r(svg,width): return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=width))).convert('RGBA')
    T1=r(t1,Wd); T2=r(t2,int(Wd*0.42)); T3=r(t3,int(Wd*0.62))
    C=crowd.resize((Wd,int(Wd*crowd.height/crowd.width)))
    gap=int(Wd*0.035)
    Ht=T1.height+gap+C.height+gap+T2.height+int(gap*0.6)+T3.height
    out=Image.new('RGBA',(Wd,Ht),(0,0,0,0)); y=0
    cy0=y+T1.height+int(gap*0.4); out.alpha_composite(C,(0,cy0)); out.alpha_composite(T1,(0,y)); y=cy0+C.height+gap
    out.alpha_composite(T2,((Wd-T2.width)//2,y)); y+=T2.height+int(gap*0.6)
    out.alpha_composite(T3,((Wd-T3.width)//2,y)); y+=T3.height
    out=out.crop((0,0,Wd,y+4)); out.save(f'{OUT}/rave_back_{cw}.png')
    print(cw,out.size)
