import sys, os, cairosvg
S=sys.argv[1]; sys.path.insert(0,S+'/scripts')
from typo import *
OUT=S+'/jersey2'; os.makedirs(OUT,exist_ok=True); INK='#000000'
def save(name, svg, wmm, dpi=300):
    open(f'{OUT}/{name}.svg','w').write(svg)
    for cw,hx in {'green':'#39FF7A','red':'#D6001C'}.items():
        cs=svg.replace('#000000',hx); open(f'{OUT}/{name}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=int(wmm/25.4*dpi))
# 1 crest: thick outer ring, thin inner ring, pixel X (7x7 blocks)
D=100; r1=47; r2=40; px=6.2; gapf=0.84; P=[]
P.append(f'<circle cx="50" cy="50" r="{r1}" fill="none" stroke="{INK}" stroke-width="5"/>')
P.append(f'<circle cx="50" cy="50" r="{r2}" fill="none" stroke="{INK}" stroke-width="2"/>')
n=7; x0=50-n*px/2
for i in range(n):
    for j in range(n):
        if i==j or i==n-1-j:
            q=px*gapf; P.append(f'<rect x="{x0+j*px+(px-q)/2:.2f}" y="{x0+i*px+(px-q)/2:.2f}" width="{q:.2f}" height="{q:.2f}" fill="{INK}"/>')
            # thicken: add neighbours to make strokes 2 blocks wide
for i in range(n-1):
    for j in (i+1, n-2-i):
        if 0<=j<n:
            q=px*gapf; P.append(f'<rect x="{x0+j*px+(px-q)/2:.2f}" y="{x0+i*px+(px-q)/2:.2f}" width="{q:.2f}" height="{q:.2f}" fill="{INK}"/>')
save('jersey_crest', f'<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 {D} {D}">{"".join(P)}</svg>', 100)
# 2 back: GATE X in square-pixel letters + 31 from 3x3 sub-blocks
W=300; P=[]
gp=5.8; txt="GATE X"; tw=(len(txt)*6-1)*gp; gx=(W-tw)/2
for i,ch in enumerate(txt):
    g=F[ch]
    for r in range(7):
        for c in range(5):
            if g[r]&(16>>c):
                q=gp*0.86; P.append(f'<rect x="{gx+(i*6+c)*gp+(gp-q)/2:.2f}" y="{r*gp+(gp-q)/2:.2f}" width="{q:.2f}" height="{q:.2f}"/>')
y=7*gp+26
sub=3; digits="31"; cols=len(digits)*6-1; p=W/(cols*sub); q=p*0.82
G3={'3':[31,1,1,7,1,1,31],'1':[12,28,12,12,12,12,30]}
for i,ch in enumerate(digits):
    g=G3.get(ch,F[ch])
    for r in range(7):
        for c in range(5):
            if g[r]&(16>>c):
                for a in range(sub):
                    for b in range(sub):
                        P.append(f'<rect x="{((i*6+c)*sub+b)*p+(p-q)/2:.2f}" y="{y+(r*sub+a)*p+(p-q)/2:.2f}" width="{q:.2f}" height="{q:.2f}"/>')
H=y+7*sub*p
save('jersey_back_gatex31', f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H:.1f}mm" viewBox="0 0 {W} {H:.2f}"><g fill="{INK}">{"".join(P)}</g></svg>', W)
# 3 pattern panel 1000 x 850 mm: aligned square grid, size grows towards bottom
PW,PH=1000,850; pitch=19; P=[]
for yy in range(0,PH,pitch):
    t=yy/PH
    s=pitch*0.41*max(0,(t-0.06)/0.94)**1.25
    if s<1.6: continue
    for xx in range(0,PW,pitch):
        P.append(f'<rect x="{xx+(pitch-s)/2:.1f}" y="{yy+(pitch-s)/2:.1f}" width="{s:.1f}" height="{s:.1f}"/>')
save('jersey_pattern', f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}"><g fill="{INK}">{"".join(P)}</g></svg>', PW, dpi=60)
print('ok', round(H,1))
