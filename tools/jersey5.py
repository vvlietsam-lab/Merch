import sys, re, json, math, cv2, numpy as np, cairosvg
S,B,ART=sys.argv[1:4]; sys.path.insert(0,S+'/scripts')
PW,PH,CX,CY=1200,1260,600,250
def inner(name):
    s=open(f'{ART}/pat_{name}_tonalblack.svg').read()
    defs=re.search(r'<defs>(.*?)</defs>',s,re.S).group(1); g=re.search(r'(<g fill.*?</g>)',s,re.S).group(1)
    defs=defs.replace('id="t"',f'id="t_{name}"'); g=g.replace('#t"',f'#t_{name}"')
    return defs,g
def combo(body,sleeve,out):
    d1,g1=inner(body); d2,g2=inner(sleeve)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}"><defs>{d1}{d2}
<clipPath id="cb"><rect x="{CX-300}" y="0" width="600" height="{PH}"/></clipPath>
<clipPath id="cs"><rect x="0" y="0" width="{CX-302}" height="{PH}"/><rect x="{CX+302}" y="0" width="{PW}" height="{PH}"/></clipPath></defs>
<g clip-path="url(#cb)"><g transform="translate(0 0)">{g1}</g><g transform="translate(0 1000)">{g1}</g></g>
<g clip-path="url(#cs)"><g>{g2}</g><g transform="translate(0 1000)">{g2}</g></g></svg>'''
    for cw,hx in {'green':'#1c4a2d','red':'#f3d0d3'}.items():
        cs=svg.replace('#4a4e52',hx); open(f'{ART}/{out}_{cw}.svg','w').write(cs)
        cairosvg.svg2png(bytestring=cs.encode(),write_to=f'{ART}/{out}_{cw}.png',output_width=3300)
for body in ['xrosette','xjacquard','tartan']:
    combo(body,'pintriple',f'jp_{body}')
print('ok')
