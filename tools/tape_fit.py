import sys, json, math, cv2, numpy as np, cairosvg
S,A,B,OUT=sys.argv[1:5]; sys.path.insert(0,S+'/scripts')
from vec import trace_mask
# motif from Sam's tape
im=cv2.imread(f'{A}/409c86ea-image.png',0); m=im<128
rows=np.where(m.any(1))[0]; band=m[rows.min():rows.max()+1]
r=np.where(band.mean(1)<0.6)[0]; mot=band[r.min():r.max()+1]; cols=np.where(mot.any(0))[0]; mot=mot[:,cols.min():cols.max()+1]
# split motif into single repeats: find column gaps
colsum=mot.any(0); gaps=np.where(~colsum)[0]
mot=cv2.resize(mot.astype(np.uint8)*255,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)>127
mw_px,mh_px,dm=trace_mask(mot,turd=20)
PW,PH,CX,CY=1200,1260,600,250
T=36.0   # tape width mm
for name in ['jersey_black_front','jersey_black_back','jersey_white_front','jersey_white_back']:
    c=json.load(open(f'{B}/{name}.json')); mp=cv2.imread(f'{B}/{name}_map.png',cv2.IMREAD_UNCHANGED); a=mp[:,:,3]>128
    ppc=c['pxPerCm']; cx,cy=c['collarX'],c['collarY']; H,W=a.shape
    body=''
    for s in (-1,1):
        pts=[]
        for dx in np.arange(7.0,60.0,0.5):    # cm from centre
            x=int(round(cx+s*dx*ppc))
            if x<0 or x>=W: break
            col=np.where(a[:,x])[0]
            if not len(col): break
            ytop=col.min()
            if (ytop-cy)/ppc>45: break
            pts.append((s*dx,(ytop-cy)/ppc))
        P=np.array(pts)
        if len(P)<10: continue
        # smooth
        k=7; ys=np.convolve(np.pad(P[:,1],(k,k),mode='edge'),np.ones(2*k+1)/(2*k+1),mode='valid'); P[:,1]=ys
        # drop the steep collar part: start where slope settles (first point at least 1.0cm below neck point minimum)
        # offset inward along normal by T/2 + 6mm
        P=P*10  # mm
        tang=np.gradient(P,axis=0); tang/=np.linalg.norm(tang,axis=1,keepdims=True)
        nrm=np.stack([-tang[:,1],tang[:,0]],1)
        if (nrm[:,1]<0).mean()>0.5: nrm=-nrm   # point down (into garment)
        off=T/2+5
        C=P+nrm*off; C[:,0]+=CX; C[:,1]+=CY
        # extend start slightly towards/under collar
        C=np.vstack([C[0]-(C[1]-C[0])*8/np.linalg.norm(C[1]-C[0]),C])
        def poly(Q): return 'M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in Q)
        tg=np.gradient(C,axis=0); tg/=np.linalg.norm(tg,axis=1,keepdims=True); nn=np.stack([-tg[:,1],tg[:,0]],1)
        body+=f'<path d="{poly(C)}" fill="none" stroke="#000000" stroke-width="{T}" stroke-linejoin="round"/>'
        for o in (T/2-4.0,-(T/2-4.0)):
            body+=f'<path d="{poly(C+nn*o)}" fill="none" stroke="#ACC" stroke-width="1.6"/>'
        # motifs along arc length
        seg=np.linalg.norm(np.diff(C,axis=0),axis=1); acc=np.concatenate([[0],np.cumsum(seg)])
        mh=T*0.56; mwid=mh*mw_px/mh_px; step=mwid*1.08
        d=step*0.6
        while d<acc[-1]-step*0.4:
            i=np.searchsorted(acc,d)-1; i=max(0,min(i,len(C)-2)); f=(d-acc[i])/seg[i]
            p=C[i]+(C[i+1]-C[i])*f; t=(C[i+1]-C[i])/seg[i]
            ang=math.degrees(math.atan2(t[1],t[0]))
            if t[0]<0: ang+=180
            body+=f'<g transform="translate({p[0]:.1f} {p[1]:.1f}) rotate({ang:.2f})"><path d="{dm}" fill="#ACC" transform="translate({-mwid/2:.2f} {-mh/2:.2f}) scale({mwid/mw_px:.5f} {mh/mh_px:.5f})"/></g>'
            d+=step
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">{body}</svg>'
    col='green' if 'black' in name else 'red'; acc_hex='#39FF7A' if col=='green' else '#D6001C'
    side=name.split('_')[-1]
    cs=svg.replace('#ACC',acc_hex)
    open(f'{OUT}/jx_tape_{col}_{side}.svg','w').write(cs)
    cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/jx_tape_{col}_{side}.png',output_width=int(PW/25.4*110))
    print(name,'ok')
