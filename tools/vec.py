import cv2, numpy as np, potrace
def trace_mask(m, turd=60, alphamax=1.0):
    """m: bool array, True=ink. returns (w,h,pathd) cropped to content with small pad."""
    ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    pad=8; m=np.pad(m[y0:y1+1,x0:x1+1],pad)
    pl=potrace.Bitmap(~m).trace(turdsize=turd,alphamax=alphamax,opticurve=True,opttolerance=0.2)
    parts=[]
    for c in pl:
        s=c.start_point; seg=[f"M{s.x:.1f} {s.y:.1f}"]
        for sg in c.segments:
            if sg.is_corner: seg.append(f"L{sg.c.x:.1f} {sg.c.y:.1f} L{sg.end_point.x:.1f} {sg.end_point.y:.1f}")
            else: seg.append(f"C{sg.c1.x:.1f} {sg.c1.y:.1f} {sg.c2.x:.1f} {sg.c2.y:.1f} {sg.end_point.x:.1f} {sg.end_point.y:.1f}")
        parts.append(" ".join(seg)+"Z")
    return m.shape[1], m.shape[0], " ".join(parts)
def ink(path, up=2):
    im=cv2.imread(path,0)
    im=cv2.resize(im,None,fx=up,fy=up,interpolation=cv2.INTER_CUBIC)
    im=cv2.GaussianBlur(im,(5,5),0)
    return im<128
def svg(w,h,d,fill="#000000"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path d="{d}" fill="{fill}" fill-rule="evenodd"/></svg>'
