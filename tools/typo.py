import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
_cache={}
def font(path):
    if path not in _cache: _cache[path]=TTFont(path)
    return _cache[path]
def text_path(txt, fpath, size, x, y, anchor='start', tracking=0.0):
    """size = font size in user units; y = baseline. returns (d, width)"""
    f=font(fpath); gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
    sc=size/upm; adv=[]; names=[]
    for ch in txt:
        g=cmap.get(ord(ch)); names.append(g); adv.append(gs[g].width*sc+tracking*size if g else size*0.5)
    w=sum(adv)-(tracking*size if txt else 0)
    x0=x-(w if anchor=='end' else w/2 if anchor=='middle' else 0)
    pen=SVGPathPen(gs); cx=x0
    for g,a in zip(names,adv):
        if g:
            tp=TransformPen(pen,(sc,0,0,-sc,cx,y)); gs[g].draw(tp)
        cx+=a
    return pen.getCommands(), w
# 5x7 dot font (same as studio)
F={'A':[14,17,17,17,31,17,17],'B':[30,17,17,30,17,17,30],'C':[14,17,16,16,16,17,14],'D':[28,18,17,17,17,18,28],'E':[31,16,16,30,16,16,31],'F':[31,16,16,30,16,16,16],'G':[14,17,16,23,17,17,15],'H':[17,17,17,31,17,17,17],'I':[14,4,4,4,4,4,14],'J':[7,2,2,2,2,18,12],'K':[17,18,20,24,20,18,17],'L':[16,16,16,16,16,16,31],'M':[17,27,21,21,17,17,17],'N':[17,17,25,21,19,17,17],'O':[14,17,17,17,17,17,14],'P':[30,17,17,30,16,16,16],'Q':[14,17,17,17,21,18,13],'R':[30,17,17,30,20,18,17],'S':[15,16,16,14,1,1,30],'T':[31,4,4,4,4,4,4],'U':[17,17,17,17,17,17,14],'V':[17,17,17,17,17,10,4],'W':[17,17,17,21,21,21,10],'X':[17,17,10,4,10,17,17],'Y':[17,17,17,10,4,4,4],'Z':[31,1,2,4,8,16,31],'0':[14,17,19,21,25,17,14],'1':[4,12,4,4,4,4,14],'2':[14,17,1,2,4,8,31],'3':[31,2,4,2,1,17,14],'4':[2,6,10,18,31,2,2],'5':[31,16,30,1,1,17,14],'6':[6,8,16,30,17,17,14],'7':[31,1,2,4,8,8,8],'8':[14,17,17,14,17,17,14],'9':[14,17,17,15,1,2,12],' ':[0]*7,'-':[0,0,0,31,0,0,0],'.':[0,0,0,0,0,12,12],':':[0,12,12,0,12,12,0]}
def dots(txt, pitch, x, y, anchor='start', r=0.42):
    n=len(txt); w=(n*6-1)*pitch
    x0=x-(w if anchor=='end' else w/2 if anchor=='middle' else 0)
    out=[]
    for i,ch in enumerate(txt):
        g=F.get(ch,F[' '])
        for row in range(7):
            for c in range(5):
                if g[row]&(16>>c):
                    cx=x0+(i*6+c+.5)*pitch; cy=y+(row+.5)*pitch
                    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{pitch*r:.2f}"/>')
    return "".join(out), w
def inner(svgtext):
    vb=re.search(r'viewBox="([^"]+)"',svgtext).group(1)
    body=re.sub(r'^.*?<svg[^>]*>','',svgtext,flags=re.S).rsplit('</svg>',1)[0]
    return vb, body
def place(svgtext, x, y, w=None, h=None, color=None):
    vb,body=inner(svgtext)
    if color: body=body.replace('#000000',color)
    _,_,vw,vh=map(float,vb.split())
    if w and not h: h=w*vh/vw
    if h and not w: w=h*vw/vh
    return f'<svg x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{vb}" preserveAspectRatio="xMidYMid meet">{body}</svg>', w, h
