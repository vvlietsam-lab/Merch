import sys, os, cv2, numpy as np, cairosvg
S=sys.argv[1]; A=sys.argv[2]; OUT=sys.argv[3]; sys.path.insert(0,S+'/scripts')
from vec import trace_mask
os.makedirs(OUT,exist_ok=True)
WAYS={'green':'#39FF7A','red':'#D6001C','tonalblack':'#4a4e52','tonalwhite':'#c9c9c4'}
# name: (file, tile width cm, turdsize, label)
P={'xrosette':('1b4d7e04',36,40,'X-rozet'),'pinbands':('f23f05ea',42,20,'Pinstripe banden'),'argylehatch':('48005452',40,10,'Argyle hatch'),
   'xjacquard':('5455bced',30,40,'X jacquard'),'tartan':('145952c3',40,10,'Tartan'),'barbed':('d0c5fcbc',40,10,'Prikkeldraad'),
   'camo':('173a88cd',32,30,'Pixel camo'),'sparkles':('f7009593',32,10,'Sterren'),'tartan2':('a60a9108',40,10,'Tartan grof'),
   'pintriple':('4ea195a0',30,10,'Pinstripe triple'),'argylefine':('1477f1c3',36,10,'Argyle fijn'),'basket':('dbe5908f',26,20,'Basket weave'),
   'xdots':('b4bb9a8b',26,20,'X stippen'),'topo':('6746ea86',40,10,'Topo lijnen')}
lib=[]
for name,(f,tw,turd,label) in P.items():
    im=cv2.imread(f'{A}/{f}-image.png',0); H,W=im.shape
    m=cv2.GaussianBlur(cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC),(3,3),0)<128
    # keep full canvas extent (no crop) so tiles butt together
    import potrace
    pl=potrace.Bitmap(~m).trace(turdsize=turd,alphamax=1.0,opticurve=True,opttolerance=0.2)
    parts=[]
    for c in pl:
        s=c.start_point; seg=[f"M{s.x:.1f} {s.y:.1f}"]
        for sg in c.segments:
            seg.append(f"L{sg.c.x:.1f} {sg.c.y:.1f} L{sg.end_point.x:.1f} {sg.end_point.y:.1f}" if sg.is_corner else f"C{sg.c1.x:.1f} {sg.c1.y:.1f} {sg.c2.x:.1f} {sg.c2.y:.1f} {sg.end_point.x:.1f} {sg.end_point.y:.1f}")
        parts.append(" ".join(seg)+"Z")
    tw_px,th_px=m.shape[1],m.shape[0]
    PW,PH=1200,1000  # mm panel
    sc=tw*10/tw_px; th=th_px*sc
    uses=[]
    y=0
    while y<PH:
        x=0
        while x<PW:
            uses.append(f'<use href="#t" x="{x/sc:.1f}" y="{y/sc:.1f}"/>'); x+=tw*10
        y+=th
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}"><defs><path id="t" d="{" ".join(parts)}" fill-rule="evenodd"/></defs><g fill="#000000" transform="scale({sc:.5f})">{"".join(uses)}</g></svg>'
    svg=svg.replace('href="#t"','href="#t" xlink:href="#t"')
    for w,hx in WAYS.items():
        cs=svg.replace('#000000',hx); open(f'{OUT}/pat_{name}_{w}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{OUT}/pat_{name}_{w}.png',output_width=2000)
    lib.append({'name':name,'label':label})
print(lib)
