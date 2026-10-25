# "scribble" all-over: loose marker X's + tiny lowercase words, mostly tonal, rare accent. Photo-space per blank.
import sys, json, math, random, cv2, numpy as np, cairosvg
S='/tmp/claude-0/-home-claude/e73f4353-fe82-5241-899e-a18cfe95ce4f/scratchpad'; ST='/home/claude/merch/studio'
sys.path.insert(0,S+'/scripts')
from typo import text_path
FN=S+'/npm/node_modules/@fontsource/'
MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
MONO6=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2'
TILE=60.0  # cm repeat
rnd=random.Random(31)
# poisson-ish scatter in tile
pts=[]
tries=0
while len(pts)<28 and tries<200000:
    tries+=1
    p=(rnd.uniform(0,TILE),rnd.uniform(0,TILE))
    if all(min(abs(p[0]-q[0]),TILE-abs(p[0]-q[0]))**2+min(abs(p[1]-q[1]),TILE-abs(p[1]-q[1]))**2>9.0**2 for q in pts): pts.append(p)
EL=[]
for i,(x,y) in enumerate(pts):
    kind='word' if i%5==2 else 'x'
    EL.append(dict(kind=kind,x=x,y=y,s=rnd.uniform(3.2,5.4),r=rnd.uniform(-28,28),acc=(i in (5,19)),
        j=[rnd.uniform(-.12,.12) for _ in range(8)],w=rnd.choice(['reversed','reversed','bass','kit 01'])))

def xmark(e, ppc):
    s=e['s']*ppc; j=e['j']; sw=0.42*ppc
    def stroke(a0,a1,b0,b1,bend):
        x0,y0=a0*s/2,a1*s/2; x1,y1=b0*s/2,b1*s/2
        mx,my=(x0+x1)/2+bend*s, (y0+y1)/2-bend*s
        return f'M{x0:.1f} {y0:.1f} Q{mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}'
    d1=stroke(-1+j[0],-1+j[1],1+j[2],1+j[3],j[4]*0.6); d2=stroke(1+j[5],-1-j[6],-1-j[7],1+j[0],-j[3]*0.6)
    return f'<path d="{d1}" stroke-width="{sw:.1f}"/><path d="{d2}" stroke-width="{sw*0.86:.1f}"/>'

def svg_for(W,H,cx,cy,ppc,tone,acc,ko=()):
    out=[]
    nx=int(math.ceil(W/ppc/TILE))+2; ny=int(math.ceil(H/ppc/TILE))+2
    for ty in range(-ny,ny):
        for tx in range(-nx,nx):
            for e in EL:
                X=cx+((tx*TILE+e['x']-18)*ppc); Y=cy+((ty*TILE+e['y'])*ppc)
                if X<-200 or X>W+200 or Y<-200 or Y>H+200: continue
                xc,yc=(X-cx)/ppc,(Y-cy)/ppc
                if any(a0-3<xc<a1+3 and b0-3<yc<b1+3 for a0,b0,a1,b1 in ko): continue
                col=acc if e['acc'] else tone
                if e['kind']=='x':
                    out.append(f'<g transform="translate({X:.1f},{Y:.1f}) rotate({e["r"]:.1f})" stroke="{col}" fill="none" stroke-linecap="round">{xmark(e,ppc)}</g>')
                else:
                    d,w=text_path(e['w'],MONO,1.15*ppc,0,0,anchor='middle',tracking=0.02)
                    out.append(f'<g transform="translate({X:.1f},{Y:.1f}) rotate({e["r"]*0.6:.1f})"><path d="{d}" fill="{col}"/></g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(out)}</svg>'

def grain(a, seed):
    r=np.random.default_rng(seed); n=r.random(a.shape).astype(np.float32)
    n=cv2.GaussianBlur(n,(0,0),0.8); n=(n-n.mean())/n.std()
    return np.clip(a*(0.82+0.18*np.clip(n*0.9+0.4,0,1)),0,255)

def render(photo, name, tone, acc, excl=(), ko=()):
    c=json.load(open(f'{ST}/{photo}.json')); W,H=c['w'],c['h']
    svg=svg_for(W,H,c['collarX'],c['collarY'],c['pxPerCm'],tone,acc,ko)
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=W)
    im=cv2.imdecode(np.frombuffer(png,np.uint8),cv2.IMREAD_UNCHANGED).astype(np.float32)
    a=im[:,:,3]; a=grain(a,len(name))
    mk=np.zeros((H,W),np.uint8)
    for poly in excl: cv2.fillPoly(mk,[np.array(poly,np.int32)],255)
    mk=cv2.GaussianBlur(mk,(0,0),1.5).astype(np.float32)/255.
    gm=cv2.imread(f'{ST}/{photo}_map.png',cv2.IMREAD_UNCHANGED)[:,:,3].astype(np.float32)/255.
    a=a*(1-mk)*gm; im[:,:,3]=a
    cv2.imwrite(f'{ST}/art/{name}.png',im.astype(np.uint8)); print(name)

def mir(poly,cx): return [(2*cx-x,y) for x,y in poly]
CUFF=[(66,602),(98,573),(302,733),(266,772)]
VNECK=[(470,228),(628,412),(786,228),(770,190),(486,190)]
CREW=[(470,175),(786,175),(776,214),(705,241),(628,246),(551,241),(480,214)]
LS_CUFF=[(0,500),(84,500),(84,620),(0,620)]
LS_CREW=[(530,330),(724,330),(712,372),(668,402),(627,408),(586,402),(542,372)]
KO_GJ={'front':[(4,3,21,19),(-23,78,-19,82)],'back':[(-15,9,15,42)]}
KO_LS={'front':[(7,7,17,12),(-64,14,-30,22),(30,14,64,22)],'back':[(-15,5,15,38)]}
T={'black':('#474b4f','#39FF7A'),'white':('#c2c2bc','#D6001C')}
SUF={'black':'green','white':'red'}
for col,(tone,acc) in T.items():
    for side,neck in (('front',VNECK),('back',CREW)):
        cx=json.load(open(f'{ST}/blanks3/gj_{col}_{side}.json'))['collarX']
        sh=(cx-628)
        pc=lambda p:[(x+sh,y) for x,y in p]
        render(f'blanks3/gj_{col}_{side}',f'pat_scribble_gj_{col}_{side}',tone,acc,[pc(CUFF),mir(pc(CUFF),cx),pc(neck)],KO_GJ[side])
        cx=json.load(open(f'{ST}/blanks2/ls_{col}_{side}.json'))['collarX']
        render(f'blanks2/ls_{col}_{side}',f'pat_scribble_ls_{col}_{side}',tone,acc,[LS_CUFF,mir(LS_CUFF,cx),[(x+cx-627,y) for x,y in LS_CREW]],KO_LS[side])

# reference repeat tile for the tech pack (42 x 42 cm, 150 dpi)
for col,(tone,acc) in T.items():
    ppc=150/2.54; Wt=int(TILE*ppc)
    sv=svg_for(Wt,Wt,0,0,ppc,tone,acc)
    open(f'{ST}/art/pat_scribble_tile_{SUF[col]}.svg','w').write(sv)
    cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{ST}/art/pat_scribble_tile_{SUF[col]}.png',output_width=Wt)

# sleeve text (longsleeve front, photo-space, along each sleeve centreline)
def sleeve_line(a, xr):
    xs,ys=[],[]
    for x in range(*xr):
        col=np.where(a[300:760,x]>128)[0]
        if len(col): xs.append(x); ys.append(300+(col.min()+col.max())/2)
    k,b=np.polyfit(xs,ys,1); return k,b
for col in ('black','white'):
    acc=T[col][1]
    for side in ('front',):
        ph=f'blanks2/ls_{col}_{side}'; c=json.load(open(f'{ST}/{ph}.json')); W,H=c['w'],c['h']; ppc=c['pxPerCm']; cx=c['collarX']
        a=cv2.imread(f'{ST}/{ph}_map.png',cv2.IMREAD_UNCHANGED)[:,:,3]
        out=[]
        for txt,xr,mid in (('reversed the bass',(110,360),235),('kit 01 · 160 bpm',(2*cx-360,2*cx-110),2*cx-235)):
            k,b=sleeve_line(a,xr); ang=math.degrees(math.atan(k)); y=k*mid+b
            d,w=text_path(txt,MONO6,2.5*ppc,0,0.36*2.5*ppc,anchor='middle',tracking=0.04)
            out.append(f'<g transform="translate({mid:.1f},{y:.1f}) rotate({ang:.2f})"><path d="{d}" fill="{acc}"/></g>')
        sv=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(out)}</svg>'
        cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{ST}/art/ls_sleevetext_{col}.png',output_width=W)
# vector files for the sleeve text (print-ready, 28 cm long each)
for suf,hx in (('green','#39FF7A'),('red','#D6001C')):
    for nm,txt in (('right','reversed the bass'),('left','kit 01 · 160 bpm')):
        d,w=text_path(txt,MONO6,25,0,20,tracking=0.04)
        open(f'{ST}/art/sleeve_{nm}_{suf}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w+2:.0f}mm" height="28mm" viewBox="0 0 {w+2:.0f} 28"><path d="{d}" fill="{hx}"/></svg>')
print('done')
