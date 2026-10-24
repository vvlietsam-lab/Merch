import sys, math, cairosvg
S,OUT=sys.argv[1:3]; sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'; COND=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-800-normal.woff2'
K='#000000'
def doc(w,h,b): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{b}</svg>'
def save(name,svg,wmm,maps,dpi=300):
    for cw,hx in maps.items():
        cs=svg.replace(K,hx); open(f'{OUT}/{name}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4000,int(wmm/25.4*dpi)))
ACC={'green':'#39FF7A','red':'#D6001C'}
xm=open(S+'/el3/x_monogram_v2.svg').read()
# 1. shield crest
W,H=160,190
shield='M10 10 H150 V95 C150 140 118 168 80 182 C42 168 10 140 10 95 Z'
inner='M22 22 H138 V95 C138 132 112 155 80 168 C48 155 22 132 22 95 Z'
B=[f'<path d="{shield}" fill="none" stroke="{K}" stroke-width="6"/>',f'<path d="{inner}" fill="none" stroke="{K}" stroke-width="2.4"/>']
p,_,_=place(xm,38,48,w=84,h=70); B.append(p)
d,_=text_path('EST · 25',COND,15,80,146,anchor='middle',tracking=0.18); B.append(f'<path d="{d}" fill="{K}"/>')
d,_=text_path('REVERSED',COND,13,80,38,anchor='middle',tracking=0.3); B.append(f'<path d="{d}" fill="{K}"/>')
save('js_crest', doc(W,H,''.join(B)), 80, ACC)
# 2. back name BASS
d,w=text_path('BASS',COND9,100,0,82,tracking=0.06)
save('name_bass', doc(round(w)+2,86,f'<path d="{d}" fill="{K}"/>'), 200, ACC)
# 3. hem band: thin double rule + 3 rows of small X marks, 1200 x 160 mm, band at top 0..110
P=[f'<rect x="0" y="0" width="1200" height="3"/>',f'<rect x="0" y="7" width="1200" height="1.2"/>']
def xmark(cx,cy,s,t):
    return ''.join(f'<rect x="{cx-s/2:.1f}" y="{cy-t/2:.1f}" width="{s}" height="{t}" transform="rotate({a} {cx:.1f} {cy:.1f})"/>' for a in (45,-45))
pitch=22
for r in range(4):
    y=24+r*pitch; off=(r%2)*pitch/2
    x=off
    while x<1200: P.append(xmark(x,y,9,2.6)); x+=pitch
P.append(f'<rect x="0" y="{24+4*pitch-6}" width="1200" height="1.2"/>')
save('js_hemband', doc(1200,160,f'<g fill="{K}">{"".join(P)}</g>'), 1200, {'green':'#2f9a58','red':'#e48d94'}, dpi=110)
print('ok')
