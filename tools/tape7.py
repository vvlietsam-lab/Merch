# X-tape that follows the garment contour in photo space (jacket sleeves, pants side seams)
import cv2, numpy as np, sys
from scipy.spatial import cKDTree
B='/home/claude/merch/studio/blanks3/'; OUT='/home/claude/merch/studio/art/'
def hexrgb(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],np.float32)

def texture(L, tw, tape, mark, pitch_k=2.0, sc=3):
    """long tape texture (RGBA), L px long, tw px wide, rendered at sc x"""
    ts=int(tw*sc); Ls=int(ts*pitch_k)
    T=np.zeros((ts,Ls,4),np.float32); T[...,:3]=tape; T[...,3]=255
    # thin inner edge lines in mark colour
    e=max(1,int(ts*0.07)); g=max(1,int(ts*0.06))
    T[g:g+e,:,:3]=mark; T[ts-g-e:ts-g,:,:3]=mark
    # X marks
    pitch=Ls; s=ts*0.42; th=max(2,ts*0.11)
    M=np.zeros((ts,Ls),np.uint8); x=pitch*0.5
    while x<Ls:
        for a in (45,-45):
            r=((x,ts/2),(s*1.414,th),a); pts=cv2.boxPoints(r).astype(np.int32); cv2.fillPoly(M,[pts],255,cv2.LINE_AA)
        x+=pitch
    m=M[...,None]/255.; T[...,:3]=T[...,:3]*(1-m)+mark*m
    return T, sc

def path_between(mask, A, Bp):
    cs,_=cv2.findContours((mask>128).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=len)[:,0,:].astype(np.float32)
    ia=np.argmin(((c-A)**2).sum(1)); ib=np.argmin(((c-Bp)**2).sum(1))
    n=len(c)
    p1=c[ia:ib+1] if ia<=ib else np.vstack([c[ia:],c[:ib+1]])
    p2=c[ib:ia+1][::-1] if ib<=ia else np.vstack([c[ib:],c[:ia+1]])[::-1]
    return p1 if len(p1)<len(p2) else p2

def resample(p, step=1.0, smooth=9):
    k=np.ones(smooth)/smooth
    pp=np.vstack([np.pad(p[:,0],(smooth//2,),mode='edge'),np.pad(p[:,1],(smooth//2,),mode='edge')]).T
    p=np.vstack([np.convolve(pp[:,0],k,'valid'),np.convolve(pp[:,1],k,'valid')]).T
    d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    s=np.arange(0,d[-1],step)
    return np.vstack([np.interp(s,d,p[:,0]),np.interp(s,d,p[:,1])]).T

def build(photo, segs, tw, inset, tape, mark, name, trim0=0, trim1=0):
    mp=cv2.imread(B+photo+'_map.png',cv2.IMREAD_UNCHANGED); a=mp[:,:,3]; H,W=a.shape
    out=np.zeros((H,W,4),np.float32)
    for A,Bp in segs:
        p=resample(path_between(a,np.array(A,np.float32),np.array(Bp,np.float32)))
        p=p[int(trim0):len(p)-int(trim1)]
        t=np.gradient(p,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6
        nrm=np.stack([-t[:,1],t[:,0]],1)
        # inward sign
        mid=len(p)//2; q=(p[mid]+nrm[mid]*8).astype(int)
        if a[q[1],q[0]]<128: nrm=-nrm
        nrm=cv2.GaussianBlur(nrm.reshape(-1,1,2).astype(np.float32),(1,0),15).reshape(-1,2); nrm/=np.linalg.norm(nrm,axis=1,keepdims=True)
        c=p+nrm*(inset+tw/2)
        c=resample(c,1.0,15)
        t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6
        nrm2=np.stack([-t[:,1],t[:,0]],1)
        if np.dot(nrm2[len(c)//2],nrm[min(len(nrm)-1,len(c)//2)])<0: nrm2=-nrm2
        T,sc=texture(len(c),tw,tape,mark)
        tree=cKDTree(c)
        band=np.zeros((H,W),np.uint8); cv2.polylines(band,[c.astype(np.int32)],False,255,int(tw+6))
        ys,xs=np.where(band>0); P=np.stack([xs,ys],1).astype(np.float32)
        _,idx=tree.query(P)
        tt=((P-c[idx])*nrm2[idx]).sum(1)  # signed across
        ok=(np.abs(tt)<=tw/2+0.7)&(idx>0)&(idx<len(c)-1)
        P,idx,tt,ys,xs=P[ok],idx[ok],tt[ok],ys[ok],xs[ok]
        u=((idx*sc)%T.shape[1]).astype(np.float32); v=((tt+tw/2)*sc).astype(np.float32)
        from scipy.ndimage import map_coordinates
        smp=np.stack([map_coordinates(T[...,k],[v,u],order=1,mode='grid-wrap') for k in range(4)],1)
        edge=np.clip(tw/2+0.7-np.abs(tt),0,1)
        smp[:,3]*=edge
        out[ys,xs]=smp
    out[...,3]*=a/255.
    rgba=np.dstack([out[...,2],out[...,1],out[...,0],out[...,3]]).clip(0,255).astype(np.uint8)
    cv2.imwrite(OUT+name+'.png',rgba); print(name)

G,Kc,R,Wc='#39FF7A','#0b0b0b','#D6001C','#f4f4f2'
for col,tape,mark in [('green',G,Kc),('red',R,Wc)]:
    tp,mk=hexrgb(tape),hexrgb(mark)
    gcol='black' if col=='green' else 'white'
    build(f'jacket_{gcol}_front',[((505,268),(45,992)),((748,268),(1214,972))],40,10,tp,mk,f'tape_jacket_front_{col}')
    build(f'jacket_{gcol}_back',[((505,212),(45,985)),((742,212),(1214,962))],40,10,tp,mk,f'tape_jacket_back_{col}')
    build(f'pants_{gcol}',[((372,122),(256,1166)),((882,122),(998,1166))],34,3,tp,mk,f'tape_pants_front_{col}')
    build(f'pants_plain_{gcol}',[((372,122),(256,1166)),((882,122),(998,1166))],34,3,tp,mk,f'tape_pants_back_{col}')
