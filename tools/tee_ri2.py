import sys, os, math, cairosvg
S=sys.argv[1]; sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
HEAD=FN+'saira/files/saira-latin-900-italic.woff2'
MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2'
OUT=S+'/tee_ri2'; os.makedirs(OUT,exist_ok=True); INK='#000000'
W=350.0; P=[]
# --- header: scale so INDUSTRIAL spans full width
f=font(HEAD); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
def adv(t,size): return sum(gs[cmap[ord(c)]].width for c in t)*size/upm
size=W/adv('INDUSTRIAL',1.0)*0.985
cap=size*0.70  # approx cap height for Saira
yb1=cap*1.12; yb2=yb1+cap*1.18
sy=1.08
d1,_=text_path('REVERSED',HEAD,size,0,0); d2,_=text_path('INDUSTRIAL',HEAD,size,0,0)
P.append(f'<path d="{d1}" fill="{INK}" transform="translate(4 {yb1*sy:.2f}) scale(1 {sy})"/>')
P.append(f'<path d="{d2}" fill="{INK}" transform="translate(0 {yb2*sy:.2f}) scale(1 {sy})"/>')
y=yb2*sy+W*0.06
# --- icon row
s=W*0.218; gap=(W-4*s)/3; sw=W*0.0075
def bx(i): return i*(s+gap)
for i in range(4):
    P.append(f'<rect x="{bx(i)+sw/2:.2f}" y="{y+sw/2:.2f}" width="{s-sw:.2f}" height="{s-sw:.2f}" fill="none" stroke="{INK}" stroke-width="{sw:.2f}"/>')
cy=y+s/2
# X
cx=bx(0)+s/2; L=s*0.66; t=s*0.15
for a in (45,-45): P.append(f'<rect x="{cx-L/2:.2f}" y="{cy-t/2:.2f}" width="{L:.2f}" height="{t:.2f}" fill="{INK}" transform="rotate({a} {cx:.2f} {cy:.2f})"/>')
# reverse arrow: thick ring open at upper-left with arrowhead pointing left at the top
cx=bx(1)+s/2; R=s*0.25; rw=s*0.12
a0=math.radians(-100); a1=math.radians(160)
x0,y0=cx+R*math.cos(a0),cy+R*math.sin(a0); x1,y1=cx+R*math.cos(a1),cy+R*math.sin(a1)
P.append(f'<path d="M{x0:.2f} {y0:.2f} A{R:.2f} {R:.2f} 0 1 1 {x1:.2f} {y1:.2f}" fill="none" stroke="{INK}" stroke-width="{rw:.2f}"/>')
ah=s*0.17
P.append(f'<polygon points="{x0-ah*1.15:.2f},{y0:.2f} {x0+ah*0.2:.2f},{y0-ah*0.85:.2f} {x0+ah*0.2:.2f},{y0+ah*0.85:.2f}" fill="{INK}"/>')
# reversed waveform: spaced rounded bars growing to the right, thin lead-in line
x0=bx(2)+s*0.12; x1=bx(2)+s*0.86; n=15; bw=s*0.034
P.append(f'<rect x="{x0:.2f}" y="{cy-s*0.008:.2f}" width="{(x1-x0)*0.32:.2f}" height="{s*0.016:.2f}" fill="{INK}"/>')
for i in range(n):
    t=i/(n-1); xx=x0+(x1-x0)*(0.18+0.82*t)
    hh=max(bw,s*0.74*(t**1.9))
    P.append(f'<rect x="{xx-bw/2:.2f}" y="{cy-hh/2:.2f}" width="{bw:.2f}" height="{hh:.2f}" rx="{bw/2:.2f}" fill="{INK}"/>')
# departure pictogram: traced plane (already includes runway line)
p,_,_=place(open(S+'/el/out/plane.svg').read(),bx(3)+s*0.1,y+s*0.14,w=s*0.8,h=s*0.7); P.append(p)
y+=s+W*0.07
# rule, text, rule
rt=W*0.006
P.append(f'<rect x="0" y="{y:.2f}" width="{W}" height="{rt:.2f}" fill="{INK}"/>'); y+=rt+W*0.045
fs=W*0.036; lp=W*0.052
for ln in ["SYSTEM: REVERSE BASS","SIGNAL: INDUSTRIAL","STATUS: READY FOR DEPARTURE"]:
    d,_=text_path(ln,MONO,fs,0,y+fs*0.70); P.append(f'<path d="{d}" fill="{INK}"/>'); y+=lp
y+=W*0.005
P.append(f'<rect x="0" y="{y:.2f}" width="{W}" height="{rt:.2f}" fill="{INK}"/>'); y+=rt+W*0.04
# dot-matrix line, rounded-square dots
pitch=W*0.0098
def dm(txt,x,anchor):
    n=len(txt); w=(n*6-1)*pitch; x0=x-(w if anchor=='end' else 0); out=[]
    for i,ch in enumerate(txt):
        g=F.get(ch,F[' '])
        for r in range(7):
            for c in range(5):
                if g[r]&(16>>c):
                    q=pitch*0.82; out.append(f'<rect x="{x0+(i*6+c)*pitch+(pitch-q)/2:.2f}" y="{y+r*pitch+(pitch-q)/2:.2f}" width="{q:.2f}" height="{q:.2f}" rx="{q*0.3:.2f}"/>')
    return ''.join(out)
P.append(f'<g fill="{INK}">{dm("160 BPM",0,"start")}{dm("GATE X",W,"end")}</g>'); y+=7*pitch
H=y+1
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}mm" height="{H:.1f}mm" viewBox="0 0 {W} {H:.2f}">{"".join(P)}</svg>'
open(f'{OUT}/ri_back_master.svg','w').write(svg)
for name,hx in {'green':'#39FF7A','red':'#D6001C'}.items():
    cs=svg.replace('#000000',hx); open(f'{OUT}/reversed_industrial_back_{name}.svg','w').write(cs)
    cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/reversed_industrial_back_{name}_300dpi.png',output_width=int(W/25.4*300))
from PIL import Image
ims=[]
for name,bg in {'green':(20,20,22),'red':(244,244,241)}.items():
    im=Image.open(f'{OUT}/reversed_industrial_back_{name}_300dpi.png').convert('RGBA'); im.thumbnail((700,700))
    c=Image.new('RGBA',(im.width+80,im.height+80),bg+(255,)); c.alpha_composite(im,(40,40)); ims.append(c.convert('RGB'))
ref=Image.open('/mnt/user-data/attachments/e73f4353-fe82-5241-899e-a18cfe95ce4f/44ea0679-image.png').convert('RGB').crop((200,200,700,700)).resize((ims[0].height,ims[0].height))
s=Image.new('RGB',(ref.width+ims[0].width+ims[1].width,ims[0].height),'white'); s.paste(ref,(0,0)); s.paste(ims[0],(ref.width,0)); s.paste(ims[1],(ref.width+ims[0].width,0)); s.save(f'{OUT}/compare.png')
print(W,round(H,1))
