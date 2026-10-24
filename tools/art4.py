import sys, os, math, cairosvg
S=sys.argv[1]; OUT=sys.argv[2]; sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
K='#000000'
WAYS={'green':'#39FF7A','red':'#D6001C','tonalblack':'#3a3d40','tonalwhite':'#dcdcd8'}
def svgdoc(w,h,body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{body}</svg>'
def save(name, svg, wmm, ways, dpi=300):
    open(f'{OUT}/{name}.svg','w').write(svg)
    for w in ways:
        cs=svg.replace(K,WAYS[w]); open(f'{OUT}/{name}_{w}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{w}.png',output_width=min(4000,int(wmm/25.4*dpi)))
# 1. tonal micro pixel grid all-over (jersey), 1200x1000mm
P=[];pitch=8;q=2.2
for y in range(0,1000,pitch):
    for x in range(0,1200,pitch): P.append(f'<rect x="{x+(pitch-q)/2}" y="{y+(pitch-q)/2}" width="{q}" height="{q}"/>')
save('pat_microgrid', svgdoc(1200,1000,f'<g fill="{K}">{"".join(P)}</g>'), 1200, ['tonalblack','tonalwhite'], dpi=50)
# 2. accent fade only lower part (jersey), 1000x850: dots grow in bottom 55%
P=[];pitch=19
for y in range(0,850,pitch):
    t=y/850; s=pitch*0.44*max(0,(t-0.45)/0.55)**1.1
    if s<1.6: continue
    for x in range(0,1000,pitch): P.append(f'<rect x="{x+(pitch-s)/2:.1f}" y="{y+(pitch-s)/2:.1f}" width="{s:.1f}" height="{s:.1f}"/>')
save('pat_ledfade_low', svgdoc(1000,850,f'<g fill="{K}">{"".join(P)}</g>'), 1000, ['green','red'], dpi=60)
# 3. pixel sash: diagonal band of pixels, 700x800mm box, band 130mm wide, from top-left to bottom-right (viewer)
W,H=700,800;pitch=10;q=7.6;band=135;P=[]
ang=math.atan2(H,W); nx,ny=-math.sin(ang),math.cos(ang)
for y in range(0,H,pitch):
    for x in range(0,W,pitch):
        cx,cy=x+pitch/2,y+pitch/2; d=abs((cx-0)*nx+(cy-0)*ny)
        if d<band/2:
            edge=band/2-d; s=q if edge>pitch*1.2 else q*max(0.35,edge/(pitch*1.2))
            P.append(f'<rect x="{cx-s/2:.1f}" y="{cy-s/2:.1f}" width="{s:.1f}" height="{s:.1f}"/>')
save('sash_pixel', svgdoc(W,H,f'<g fill="{K}">{"".join(P)}</g>'), W, ['green','red'], dpi=100)
# 4. sleeve number 31 small pixel (reuse font)
P=[];p=2.0;g3={'3':[31,1,1,7,1,1,31],'1':[12,28,12,12,12,12,30]}
for i,ch in enumerate('31'):
    for r in range(7):
        for c in range(5):
            if g3[ch][r]&(16>>c): P.append(f'<rect x="{(i*6+c)*p+0.15}" y="{r*p+0.15}" width="{p-0.3}" height="{p-0.3}"/>')
save('sleeve31', svgdoc(22,14,f'<g fill="{K}">{"".join(P)}</g>'), 60, ['green','red'])
# 5. tonal reversed waveform (tee back), 600x320mm: bars growing to the right, symmetric
W,H=600,320;P=[];n=60;bw=4.6
for i in range(n):
    t=i/(n-1); x=10+i*(W-20)/(n-1); h=max(3,(H-10)*(t**2.0)*(0.75+0.25*math.sin(i*1.7)**2))
    P.append(f'<rect x="{x-bw/2:.1f}" y="{H/2-h/2:.1f}" width="{bw}" height="{h:.1f}" rx="{bw/2}"/>')
P.append(f'<rect x="0" y="{H/2-0.9}" width="{W*0.35}" height="1.8"/>')
save('wave_tonal', svgdoc(W,H,f'<g fill="{K}">{"".join(P)}</g>'), W, ['tonalblack','tonalwhite'], dpi=150)
# 6. spec frame: crop marks + ticks + micro labels, 440x420mm
W,H=440,420;L=30;t=1.4;P=[]
for (x,y,sx,sy) in [(0,0,1,1),(W,0,-1,1),(0,H,1,-1),(W,H,-1,-1)]:
    P.append(f'<rect x="{min(x,x+sx*L)}" y="{y-(t if sy<0 else 0)}" width="{L}" height="{t}"/>')
    P.append(f'<rect x="{x-(t if sx<0 else 0)}" y="{min(y,y+sy*L)}" width="{t}" height="{L}"/>')
for i in range(1,10):
    x=i*W/10; P.append(f'<rect x="{x-0.5}" y="0" width="1" height="{8 if i%5 else 14}"/>')
for i in range(1,10):
    y=i*H/10; P.append(f'<rect x="{W-(8 if i%5 else 14)}" y="{y-0.5}" width="{8 if i%5 else 14}" height="1"/>')
for txt,x,y,a in [('REV-IND / 001',L+8,10,'start'),('160 BPM',W-L-8,H-4,'end'),('X',W/2,H-4,'middle')]:
    d,_=text_path(txt,MONO,8,x,y,anchor=a,tracking=0.1); P.append(f'<path d="{d}"/>')
save('spec_frame', svgdoc(W,H,f'<g fill="{K}">{"".join(P)}</g>'), W, ['green','red'], dpi=150)
print('ok')
