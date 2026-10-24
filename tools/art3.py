import sys, os, math, cairosvg, re
S=sys.argv[1]; OUT=sys.argv[2]; sys.path.insert(0,S+'/scripts')
from typo import *
os.makedirs(OUT,exist_ok=True)
FN=S+'/npm/node_modules/@fontsource/'
ARCH=FN+'archivo/files/archivo-latin-900-italic.woff2'
COND=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-800-normal.woff2'
COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'
MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
K='#000000'
def svgdoc(w,h,body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{body}</svg>'
WAYS={'green':'#39FF7A','red':'#D6001C','tonalblack':'#4a4e52','tonalwhite':'#c4c4bf'}
def save(name, svg, wmm, ways, dpi=300):
    open(f'{OUT}/{name}.svg','w').write(svg)
    for w in ways:
        cs=svg.replace(K,WAYS[w]); open(f'{OUT}/{name}_{w}.svg','w').write(cs)
        px=min(4000,int(wmm/25.4*dpi)); cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{w}.png',output_width=px)
def bbox_text(t,f,size):
    d,w=text_path(t,f,size,0,0); return d,w
# ---------- 1. argyle pinstripe panel (mm) ----------
PW,PH=1200,1000; pitch=10.0; base=0.8; mx=7.2; A,B=80,115
def nearest(x,y):
    best=9
    for j in range(int(y//B)-1,int(y//B)+3):
        off=(A if j%2 else 0)
        for i in range(int((x-off)//(2*A))-1,int((x-off)//(2*A))+3):
            cx=off+i*2*A; cy=j*B
            d=abs(x-cx)/A+abs(y-cy)/B; best=min(best,d)
    return best
paths=[]
x=pitch/2
while x<PW:
    L=[];R=[]
    y=0
    while y<=PH:
        d=nearest(x,y); w=base+(mx-base)*max(0,1-d)**0.9 if d<1 else base
        L.append((x-w/2,y)); R.append((x+w/2,y)); y+=4
    pts=L+R[::-1]
    paths.append('M'+' L'.join(f'{a:.2f} {b:.1f}' for a,b in pts)+'Z')
    x+=pitch
save('pat_argyle', svgdoc(PW,PH,f'<path d="{" ".join(paths)}" fill="{K}"/>'), PW, ['tonalblack','tonalwhite'], dpi=60)
# ---------- 2. side stripe: two bars 1.2 + 0.5 cm, gap 0.5 ----------
H=480
save('side_stripe', svgdoc(22,H,f'<rect x="0" y="0" width="12" height="{H}" fill="{K}"/><rect x="17" y="0" width="5" height="{H}" fill="{K}"/>'), 22, ['green','red'])
# ---------- 3. wordmark reversed™ ----------
d,w=text_path('reversed',ARCH,100,0,100); tm,tw=text_path('™',ARCH,38,w+4,52)
save('wm_reversed', svgdoc(round(w+tw+8),128,f'<path d="{d} {tm}" fill="{K}"/>'), 240, ['green','red','tonalblack','tonalwhite'])
# ---------- 4. crest: double ring + X monogram + ring text ----------
xm=open(S+'/el3/x_monogram_v2.svg').read()
D=200; c=100; body=[f'<circle cx="{c}" cy="{c}" r="96" fill="none" stroke="{K}" stroke-width="6"/>',f'<circle cx="{c}" cy="{c}" r="66" fill="none" stroke="{K}" stroke-width="3"/>']
p,_,_=place(xm,c-40,c-34,w=80,h=68); body.append(p)
f=font(COND); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
txt='REVERSED INDUSTRIAL · EST. 2025 · '; size=19; r=80; sc=size/upm
advs=[gs[cmap[ord(ch)]].width*sc+1.2 for ch in txt]; total=sum(advs); ang=-math.pi/2 - (total/r)/2*0
a=-math.pi/2 - (total/(2*r))
for ch,ad in zip(txt,advs):
    g=cmap.get(ord(ch)); mid=a+ad/2/r
    if g and ch!=' ':
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        pen=SVGPathPen(gs); gw=gs[g].width*sc
        tp=TransformPen(pen,(sc,0,0,-sc,-gw/2,size*0.36)); gs[g].draw(tp)
        X=c+r*math.cos(mid); Y=c+r*math.sin(mid); rot=math.degrees(mid)+90
        body.append(f'<path d="{pen.getCommands()}" fill="{K}" transform="translate({X:.2f} {Y:.2f}) rotate({rot:.2f})"/>')
    a+=ad/r
save('crest_ring', svgdoc(D,D,''.join(body)), 90, ['green','red'])
# ---------- 5. back name bar REVERSED (condensed caps) ----------
d,w=text_path('REVERSED',COND9,100,0,82,tracking=0.04)
save('name_reversed', svgdoc(round(w)+2,86,f'<path d="{d}" fill="{K}"/>'), 260, ['green','red'])
# ---------- 6. number 31 recolorable ----------
n31=open(S+'/el3/number_31.svg').read(); open(f'{OUT}/num31.svg','w').write(n31)
vb=re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',n31); save('num31', n31.replace('<svg ',f'<svg width="{vb.group(1)}" height="{vb.group(2)}" ',1), 300, ['green','red'])
# ---------- 7. X monogram small ----------
open(f'{OUT}/xmono.svg','w').write(xm); save('xmono', xm, 80, ['green','red','tonalblack','tonalwhite'])
# ---------- 8. hem micro label ----------
l1,w1=text_path('REVERSED INDUSTRIAL™',MONO,10,0,9); l2,w2=text_path('THINKING IN REVERSE — 155/160',MONO,10,0,24)
W=max(w1,w2)+1
save('hem_micro', svgdoc(round(W),28,f'<path d="{l1} {l2}" fill="{K}"/>'), 90, ['green','red','tonalblack','tonalwhite'])
# ---------- 9. X-back tee: full back layout ----------
W=320; P=[]; y=0
for t in ['BUILT FROM','REVERSED SOUND']:
    d,tw=text_path(t,COND,13,W/2,y+11,anchor='middle',tracking=0.18); P.append(f'<path d="{d}" fill="{K}"/>'); y+=16
y+=14; p,_,mh=place(xm,W/2-95,y,w=190); P.append(p); y+=mh+18
d,ww=text_path('reversed industrial',ARCH,34,0,0)
s=W*0.86/ww; d,ww=text_path('reversed industrial',ARCH,34*s,W/2,y+30*s,anchor='middle'); P.append(f'<path d="{d}" fill="{K}"/>')
tm,_=text_path('™',ARCH,12*s,W/2+ww/2+2,y+12*s); P.append(f'<path d="{tm}" fill="{K}"/>'); y+=40*s+12
d,_=text_path('THINKING IN REVERSE',MONO,9,W/2,y+8,anchor='middle',tracking=0.12); P.append(f'<path d="{d}" fill="{K}"/>'); y+=22
P.append(f'<rect x="{W/2-40}" y="{y}" width="80" height="0.8" fill="{K}"/>'); y+=14
for t in ['IT STARTS AT THE END. A SOUND PULLED BACKWARDS','UNTIL IT HITS HARDER THAN IT BEGAN.','MADE FOR THE ROOMS NOBODY LEAVES.']:
    d,_=text_path(t,MONO,7.2,W/2,y+6,anchor='middle'); P.append(f'<path d="{d}" fill="{K}"/>'); y+=11
save('xback_layout', svgdoc(W,round(y+2),''.join(P)), W, ['green','red'])
print('ok')
