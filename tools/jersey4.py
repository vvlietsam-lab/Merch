import sys, os, math, json, cv2, numpy as np, cairosvg
S,B,OUT=sys.argv[1:4]; sys.path.insert(0,S+'/scripts')
from typo import *
FN=S+'/npm/node_modules/@fontsource/'
COND9=FN+'saira-semi-condensed/files/saira-semi-condensed-latin-900-normal.woff2'; MONO=FN+'ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2'
K='#000000'; PW,PH,CX,CY=1200,1260,600,250
def doc(w,h,b): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{b}</svg>'
def save(name,svg,wmm,maps,dpi=300):
    for cw,rep in maps.items():
        cs=svg
        for a,b in rep.items(): cs=cs.replace(a,b)
        open(f'{OUT}/{name}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/{name}_{cw}.png',output_width=min(4200,int(wmm/25.4*dpi)))
MUTED={'green':{K:'#2b7a48'},'red':{K:'#e8a3a8'}}
# 1. BODY: rows of the reversed-kick envelope. Bars grow from silence into one spike, then cut. Every other row runs the other way (reversed).
P=[]; row_h=118; pitch=9.0; bw=3.4; n_per=24
y=CY-60
r=0
while y<PH:
    cyr=y+row_h/2; seg_w=n_per*pitch; x0=CX-300-((r%2)*seg_w/2)
    x=x0
    while x<CX+300:
        for i in range(n_per):
            t=i/(n_per-1); t=t if r%2==0 else 1-t
            h=max(bw, row_h*0.86*(t**2.2)*(0.5+0.5*abs(math.sin(i*1.9+r))))
            bx=x+i*pitch
            if CX-300<bx<CX+300-bw:
                P.append(f'<rect x="{bx:.1f}" y="{cyr-h/2:.1f}" width="{bw}" height="{h:.1f}" rx="{bw/2}"/>')
        x+=seg_w+pitch*2
    y+=row_h; r+=1
# 2. SLEEVES: LED dot grid (unlit board), round dots
for s in (-1,1):
    x=CX+s*(300+6)
    while 0<x<PW:
        yy=0
        while yy<PH:
            P.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="1.9"/>'); yy+=7
        x+=s*7
save('jw_body', doc(PW,PH,f'<g fill="{K}">{"".join(P)}</g>'), PW, MUTED, dpi=70)
# 3. SHOULDER: dot-matrix text running along the real shoulder seam (per photo)
def path_for(name):
    c=json.load(open(f'{B}/{name}.json')); a=cv2.imread(f'{B}/{name}_map.png',cv2.IMREAD_UNCHANGED)[:,:,3]>128
    ppc=c['pxPerCm']; cx,cy=c['collarX'],c['collarY']; H,W=a.shape; res=[]
    for s in (-1,1):
        pts=[]
        for dx in np.arange(8.0,60.0,0.5):
            x=int(round(cx+s*dx*ppc))
            if x<0 or x>=W: break
            col=np.where(a[:,x])[0]
            if not len(col) or (col.min()-cy)/ppc>45: break
            pts.append((s*dx,(col.min()-cy)/ppc))
        Pp=np.array(pts); k=7; Pp[:,1]=np.convolve(np.pad(Pp[:,1],(k,k),mode='edge'),np.ones(2*k+1)/(2*k+1),mode='valid'); Pp*=10
        tg=np.gradient(Pp,axis=0); tg/=np.linalg.norm(tg,axis=1,keepdims=True); nr=np.stack([-tg[:,1],tg[:,0]],1)
        if (nr[:,1]<0).mean()>0.5: nr=-nr
        C=Pp+nr*24; C[:,0]+=CX; C[:,1]+=CY; res.append((s,C))
    return res
TXT='REVERSED INDUSTRIAL  X  155-160  X  '
pitch=3.1; dot=1.25
for name in ['jersey_black_front','jersey_black_back','jersey_white_front','jersey_white_back']:
    body=''
    for s,C in path_for(name):
        seg=np.linalg.norm(np.diff(C,axis=0),axis=1); acc=np.concatenate([[0],np.cumsum(seg)])
        txt=TXT*3; adv=6*pitch; d=20.0; i=0
        # direction: always read from collar outward
        while d<acc[-1]-adv and i<len(txt):
            ch=txt[i]; g=F.get(ch,F[' '])
            j=min(np.searchsorted(acc,d)-1,len(C)-2); j=max(0,j); f=(d-acc[j])/seg[j]; p=C[j]+(C[j+1]-C[j])*f; t=(C[j+1]-C[j])/seg[j]
            ang=math.degrees(math.atan2(t[1],t[0]))
            flip=False
            if t[0]<0: ang+=180; flip=True
            dots=[]
            for rr in range(7):
                for cc in range(5):
                    if g[rr]&(16>>cc):
                        lx=(4-cc)*pitch if flip else cc*pitch
                        dots.append(f'<circle cx="{lx:.2f}" cy="{(rr-3)*pitch:.2f}" r="{dot}"/>')
            if dots:
                body+=f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({ang:.2f})">{"".join(dots)}</g>'
            d+=adv; i+=1
    col='green' if 'black' in name else 'red'; side=name.split('_')[-1]
    sv=doc(PW,PH,f'<g fill="#ACC">{body}</g>').replace('#ACC','#39FF7A' if col=='green' else '#D6001C')
    open(f'{OUT}/jw_shoulder_{col}_{side}.svg','w').write(sv); cairosvg.svg2png(bytestring=sv.encode(),write_to=f'{OUT}/jw_shoulder_{col}_{side}.png',output_width=int(PW/25.4*120))
# 4. CREST: rounded-square LED badge with lit X (unlit dots dim)
n=9; pt=8; D=n*pt+28; B2=[f'<rect x="3" y="3" width="{D-6}" height="{D-6}" rx="14" fill="none" stroke="#ACC" stroke-width="4"/>']
for yy in range(n):
    for xx in range(n):
        on=abs(xx-yy)<=1 and (xx-yy)!=-2 or abs(xx-(n-1-yy))<=0 or xx==yy
        on=(xx==yy) or (xx==n-1-yy) or (abs(xx-yy)==1 and 1<=xx<=n-2 and 1<=yy<=n-2) or (abs(xx-(n-1-yy))==1 and 1<=xx<=n-2 and 1<=yy<=n-2)
        B2.append(f'<circle cx="{14+xx*pt+pt/2}" cy="{14+yy*pt+pt/2}" r="{pt*0.38}" fill="{"#ACC" if on else "#DIM"}"/>')
cr=doc(D,D,''.join(B2))
save('jw_crest', cr, 80, {'green':{'#ACC':'#39FF7A','#DIM':'#1d3a27'},'red':{'#ACC':'#D6001C','#DIM':'#f1c9cc'}})
# 5. BACK small line under the number + neck BPM
d,w=text_path('THINKING IN REVERSE',MONO,10,0,9,tracking=0.2)
save('jw_backline', doc(round(w)+2,12,f'<path d="{d}" fill="{K}"/>'), 140, {'green':{K:'#39FF7A'},'red':{K:'#D6001C'}})
dl,w2=dots_txt=None,None
from typo import dots
dd,ww=dots('160 BPM',2.2,0,0)
save('jw_neckbpm', doc(round(ww)+1,16,f'<g fill="{K}">{dd}</g>'), 60, {'green':{K:'#39FF7A'},'red':{K:'#D6001C'}})
print('ok')
