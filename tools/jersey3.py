import sys, os, math, cv2, numpy as np, cairosvg
S=sys.argv[1]; A=sys.argv[2]; OUT=sys.argv[3]; sys.path.insert(0,S+'/scripts')
from typo import *; from vec import trace_mask
FN=S+'/npm/node_modules/@fontsource/'
ARCH=FN+'archivo/files/archivo-latin-900-italic.woff2'; COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'
COND=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-800-normal.woff2'; MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
K='#000000'; W2='#FFFFFF'
def doc(w,h,b): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{b}</svg>'
def save(name,svg,wmm,maps,dpi=300):
    for cw,rep in maps.items():
        cs=svg
        for a,b in rep.items(): cs=cs.replace(a,b)
        open(f'{OUT}/{name}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4200,int(wmm/25.4*dpi)))
# panel coords: mm, x0 = centre at 600, y0 = 250 (=collar). width 1200, height 1100
PW,PH,CX,CY=1200,1260,600,250
# ---- 1. body argyle with fading vertical stripes + sleeve pinstripes ----
P=[]; Aw,Bh=95,135   # half-diagonals mm
pitch=8.0
def diamond_t(x,y):
    # returns (inside_striped, t) ; checkerboard diamonds centred on lattice
    u=(x-CX)/Aw; v=(y-CY-40)/Bh
    a=u+v; b=v-u; ia,ib=math.floor(a),math.floor(b)
    striped=(ia+ib)%2==0
    fa,fb=a-ia,b-ib   # position inside diamond 0..1
    t=(fa+fb)/2       # 0 top tip .. 1 bottom tip
    return striped,t
xs=np.arange(CX-300+pitch/2, CX+300, pitch)
for x in xs:
    y=0.0; seg=None
    while y<=PH:
        st,t=diamond_t(x,y)
        w=(0.6+3.6*t**1.6) if st else 0
        if w>0.4:
            P.append(f'<rect x="{x-w/2:.2f}" y="{y:.1f}" width="{w:.2f}" height="3.05"/>')
        y+=3
# sleeves |x|>300mm: uniform pinstripes fading lighter towards cuff
for side in (-1,1):
    x=CX+side*(300+pitch/2)
    while 0<x<PW:
        P.append(f'<rect x="{x-0.8:.2f}" y="0" width="1.6" height="{PH}"/>'); x+=side*pitch*0.75
save('jx_body', doc(PW,PH,f'<g fill="{K}">{"".join(P)}</g>'), PW, {'green':{K:'#2b7a48'},'red':{K:'#e8a3a8'}}, dpi=70)
# ---- 2. shoulder tape (own design): black band, accent pipings, accent chevron-X motif from Sam's tape ----
im=cv2.imread(f'{A}/409c86ea-image.png',0); m=im<128
rows=np.where(m.any(1))[0]; band=m[rows.min():rows.max()+1]
# motif = rows between the two border lines
r=np.where(band.mean(1)<0.6)[0]; mot=band[r.min():r.max()+1]
cols=np.where(mot.any(0))[0]; mot=mot[:,cols.min():cols.max()+1]
mot=cv2.resize(mot.astype(np.uint8)*255,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)>127
w,h,dm=trace_mask(mot,turd=20)
L=620; T=38   # tape length/width mm
mh=T*0.58; mw=mh*w/h
reps=int(L/mw)+1
tape=f'<rect x="0" y="0" width="{L}" height="{T}" fill="{K}"/><rect x="0" y="3" width="{L}" height="1.6" fill="#ACC"/><rect x="0" y="{T-4.6}" width="{L}" height="1.6" fill="#ACC"/>'
tape+=''.join(f'<path d="{dm}" fill="#ACC" transform="translate({i*mw:.2f} {(T-mh)/2:.2f}) scale({mw/w:.5f} {mh/h:.5f})"/>' for i in range(reps))
def tape_on(x0,y0,x1,y1,flip):
    ang=math.degrees(math.atan2(y1-y0,x1-x0))
    return f'<g transform="translate({x0:.1f} {y0:.1f}) rotate({ang:.2f}) translate(0 {-T/2})">{tape}</g>'
# shoulder line (front): neck (-100,-47) -> shoulder (-288,114) -> cuff (-480,310) mm rel. collar; tape sits 12mm inside the top edge
t=''
for s in (-1,1):
    x0,y0=CX+s*95,CY-30; x1,y1=CX+s*500,CY+330
    t+=tape_on(x0,y0,x1,y1,s)
save('jx_tape', doc(PW,PH,t), PW, {'green':{'#ACC':'#39FF7A'},'red':{'#ACC':'#D6001C'}}, dpi=110)
# ---- 3. base polyester (solid) ----
for cw,hx in {'black':'#131416','white':'#f2f2ef'}.items():
    open(f'{OUT}/jx_base_{cw}.svg','w').write(doc(PW,PH,f'<rect width="{PW}" height="{PH}" fill="{hx}"/>'))
    cv2.imwrite(f'{OUT}/jx_base_{cw}.png', np.full((40,44,3), [int(hx[5:7],16),int(hx[3:5],16),int(hx[1:3],16)], np.uint8))
# ---- 4. sponsor 'reversed' in white/black ----
d,ww=text_path('reversed',ARCH,100,0,100)
save('jx_sponsor', doc(round(ww)+4,128,f'<path d="{d}" fill="{K}"/>'), 260, {'white':{K:'#F4F4F2'},'black':{K:'#151515'}})
# ---- 5. crest: round, star on top, ring text, X ----
xm=open(S+'/el3/x_monogram_v2.svg').read(); c=100; B=[f'<circle cx="{c}" cy="{c+8}" r="88" fill="none" stroke="{K}" stroke-width="5"/>',f'<circle cx="{c}" cy="{c+8}" r="62" fill="none" stroke="{K}" stroke-width="2.5"/>']
p,_,_=place(xm,c-36,c-22,w=72,h=60); B.append(p)
star=' '.join(f'{c+ (9 if i%2==0 else 3.6)*math.sin(i*math.pi/5):.2f},{10+ -(9 if i%2==0 else 3.6)*math.cos(i*math.pi/5)+8:.2f}' for i in range(10))
B.append(f'<polygon points="{star}" fill="{K}"/>')
f=font(COND); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
from fontTools.pens.svgPathPen import SVGPathPen; from fontTools.pens.transformPen import TransformPen
def ring(txt,r,size,start,cy,inv=False):
    sc=size/upm; adv=[gs[cmap[ord(ch)]].width*sc+1.4 for ch in txt]; tot=sum(adv)
    a=start-(tot/(2*r))*(-1 if inv else 1); out=[]
    for ch,ad in zip(txt,adv):
        mid=a+(ad/2/r)*(-1 if inv else 1); g=cmap.get(ord(ch))
        if ch!=' ':
            pen=SVGPathPen(gs); gw=gs[g].width*sc; gs[g].draw(TransformPen(pen,(sc,0,0,-sc,-gw/2,size*0.36)))
            X=c+r*math.cos(mid); Y=cy+r*math.sin(mid); rot=math.degrees(mid)+(90 if not inv else -90)
            out.append(f'<path d="{pen.getCommands()}" fill="{K}" transform="translate({X:.2f} {Y:.2f}) rotate({rot:.2f})"/>')
        a+=(ad/r)*(-1 if inv else 1)
    return ''.join(out)
B.append(ring('REVERSED INDUSTRIAL',75,17,-math.pi/2,c+8)); B.append(ring('EST. 2025',75,15,math.pi/2,c+8,inv=True))
save('jx_crest', doc(200,200,''.join(B)), 90, {'white':{K:'#F4F4F2'},'black':{K:'#151515'}})
# ---- 6. jock tag (woven label, 2 colours: black block + accent block) ----
T=[f'<rect x="0" y="0" width="150" height="62" fill="#151515"/>',f'<rect x="4" y="4" width="62" height="54" fill="#ACC"/>']
for txt,y,sz in [('REVERSED',22,14),('INDUSTRIAL',38,10.5)]:
    d,_=text_path(txt,COND9,sz,108,y,anchor='middle',tracking=0.06); T.append(f'<path d="{d}" fill="#F4F4F2"/>')
d,_=text_path('THINKING IN REVERSE',MONO,6,108,52,anchor='middle'); T.append(f'<path d="{d}" fill="#F4F4F2"/>')
p,_,_=place(xm,13,9,w=44,h=44,color='#151515'); T.append(p)
save('jx_jocktag', doc(150,62,''.join(T)), 60, {'green':{'#ACC':'#39FF7A'},'red':{'#ACC':'#D6001C'}})
print('ok')
