"""Standing cat, exact existing OLED face pixels plus nominal electronics."""
import json
from pathlib import Path
from cat_common import *
from cat_body import gen_raw as body_shape
from cat_back import gen_raw as back_shape
from cat_c3_tray import gen_raw as tray_shape

def face_shapes():
    pixels=json.loads(Path(__file__).with_name('piku_face_pixels.json').read_text())
    runs={}
    for y,row in enumerate(pixels):
        x=0
        while x<128:
            if not row[x]:x+=1;continue
            start=x
            while x<128 and row[x]:x+=1
            runs.setdefault((start,x),[]).append(y)
    parts=[];pitch=21.74/128
    for (x0,x1),ys in runs.items():
        start=last=ys[0]
        for y in ys[1:]+[999]:
            if y==last+1:last=y;continue
            p=Pos(((x0+x1)/2-64)*pitch,OLED_Y+(32-(start+last+1)/2)*pitch,OLED_FRONT-2.96)*Box(
                (x1-x0)*pitch,(last-start+1)*pitch,0.04,align=(Align.CENTER,Align.CENTER,Align.MIN))
            p.label='OLED_face_pixel';p.color=Color(0.36,0.84,0.95);parts.append(p)
            start=last=y
    return parts

def raw_parts(include_back=True,include_face=True):
    parts=[body_shape(),tray_shape()]+nominal_oled()+nominal_touch()+nominal_c3()
    if include_back:parts.insert(1,back_shape())
    if include_face:parts+=face_shapes()
    return parts

def gen_step():
    return Compound(label='Piku_the_little_cat',children=[STAND*p for p in raw_parts()])
