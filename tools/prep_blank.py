import sys, json, cv2, numpy as np
src, out, chest_cm = sys.argv[1], sys.argv[2], float(sys.argv[3])
im=cv2.imread(src); H,W=im.shape[:2]
lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB); L=lab[:,:,0].astype(np.float32)
border=np.concatenate([L[:20].ravel(),L[-20:].ravel(),L[:,:20].ravel(),L[:,-20:].ravel()])
bg=np.median(border); center=L[H//2-40:H//2+40, W//2-40:W//2+40].mean(); dark=center<bg
d=(bg-L) if dark else (L-bg)
seed=(cv2.GaussianBlur(d,(0,0),3)>abs(center-bg)*0.45).astype(np.uint8)
n,labs,st,_=cv2.connectedComponentsWithStats(seed,8); k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); seed=(labs==k).astype(np.uint8)
gc=np.full((H,W),cv2.GC_PR_BGD,np.uint8)
gc[cv2.erode(seed,np.ones((25,25),np.uint8))>0]=cv2.GC_FGD
gc[cv2.dilate(seed,np.ones((5,5),np.uint8))>0]=np.where(gc[cv2.dilate(seed,np.ones((5,5),np.uint8))>0]==cv2.GC_FGD,cv2.GC_FGD,cv2.GC_PR_FGD)
gc[:8,:]=cv2.GC_BGD; gc[-8:,:]=cv2.GC_BGD; gc[:,:8]=cv2.GC_BGD; gc[:,-8:]=cv2.GC_BGD
bgm=np.zeros((1,65),np.float64); fgm=np.zeros((1,65),np.float64)
cv2.grabCut(im,gc,None,bgm,fgm,6,cv2.GC_INIT_WITH_MASK)
m=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
n,labs,st,_=cv2.connectedComponentsWithStats(m,8); k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(labs==k).astype(np.uint8)
ff=m.copy(); cv2.floodFill(ff,None,(0,0),1); m=m|(1-ff)
if not dark and (len(sys.argv)<6 or sys.argv[5]!="nolo"):
    lo=(cv2.GaussianBlur(L,(0,0),4)<center-22).astype(np.uint8)
    m=m&(1-lo); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    n,labs,st,_=cv2.connectedComponentsWithStats(m,8); k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(labs==k).astype(np.uint8)
    ff=m.copy(); cv2.floodFill(ff,None,(0,0),1); m=m|(1-ff)
if dark:
    sh=(cv2.GaussianBlur(L,(0,0),4)>center+(bg-center)*0.33).astype(np.uint8)
    m=m&(1-sh); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    n,labs,st,_=cv2.connectedComponentsWithStats(m,8); k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(labs==k).astype(np.uint8)
    ff=m.copy(); cv2.floodFill(ff,None,(0,0),1); m=m|(1-ff)
ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
cx=int(np.median(xs))
# collar: top-most garment pixel in the central column band
band=m[:, cx-int((x1-x0)*0.12):cx+int((x1-x0)*0.12)]; collar_y=int(np.argmax(band.any(axis=1)))
# chest width: measure body width at 62% of garment height (below armpits, sleeves excluded)
yy=int(y0+(y1-y0)*0.62); row=np.where(m[yy])[0]
# take run containing cx
runs=np.split(row, np.where(np.diff(row)>1)[0]+1); run=[r for r in runs if r.min()<=cx<=r.max()][0]
chest_px=run.max()-run.min(); pxcm=chest_px/chest_cm
# shading & displacement
Lb=cv2.GaussianBlur(L,(0,0),float(sys.argv[4]) if len(sys.argv)>4 else 2.0); Lm=cv2.GaussianBlur(L*m,(0,0),40)/np.maximum(cv2.GaussianBlur(m.astype(np.float32),(0,0),40),1e-3)
shade=np.clip(Lb/np.maximum(Lm,1.0),0.3,1.7) if not dark else np.clip((Lb+18)/np.maximum(Lm+18,1.0),0.3,1.7)
R=np.clip(shade*128,0,255)
Ld=cv2.GaussianBlur(L,(0,0),6)
gx=cv2.Sobel(Ld,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(Ld,cv2.CV_32F,0,1,ksize=3)
sc=40.0/ (np.percentile(np.abs(np.concatenate([gx[m>0],gy[m>0]])),98)+1e-3)
G=np.clip(128+gx*sc,0,255); B=np.clip(128+gy*sc,0,255)
A=cv2.GaussianBlur(m.astype(np.float32)*255,(0,0),1.2)
mp=np.dstack([B,G,R,A]).astype(np.uint8)  # BGRA for cv2 -> stored as RGBA R=shade G=dx B=dy
cv2.imwrite(out+'_map.png', mp)
cv2.imwrite(out+'.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 92])
cal={'w':W,'h':H,'collarX':cx,'collarY':collar_y,'pxPerCm':round(pxcm,3),'dark':bool(dark),'chestCm':chest_cm,'bbox':[int(x0),int(y0),int(x1),int(y1)]}
json.dump(cal,open(out+'.json','w')); print(out.split('/')[-1],cal)
