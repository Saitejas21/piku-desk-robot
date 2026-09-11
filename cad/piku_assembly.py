"""Piku assembly. Screen and artwork are preview only; print body and back.
Body rear Z=32, lid exterior Z=34; all parts stand on the paw datum Y=-28.5.
Face pixels match the firmware bitmap at the OLED's nominal active size.
"""
import json
from pathlib import Path
from build123d import *
from piku_body import gen_step as body_shape,WINDOW_W,WINDOW_H,WINDOW_Y
from piku_back import gen_step as back_shape

def gen_step():
    body=body_shape()
    back=Pos(0,0,34)*Rot(0,180,0)*back_shape()
    screen=Pos(0,WINDOW_Y,-0.03)*extrude(RectangleRounded(WINDOW_W-0.2,WINDOW_H-0.2,2.9),amount=0.04)
    screen.label='oled_preview_only'
    screen.color=Color(0.025,0.035,0.045)
    parts=[body,back,screen]
    pixels=json.loads(Path(__file__).with_name('piku_face_pixels.json').read_text())
    # Vertically merge identical horizontal runs to keep the STEP compact.
    runs={}
    for y,row in enumerate(pixels):
        x=0
        while x<128:
            if not row[x]: x+=1; continue
            start=x
            while x<128 and row[x]:x+=1
            runs.setdefault((start,x),[]).append(y)
    pitch=21.74/128
    for (x0,x1),ys in runs.items():
        start=last=ys[0]
        for y in ys[1:]+[999]:
            if y==last+1: last=y; continue
            px=((x0+x1)/2-64)*pitch
            py=WINDOW_Y+(32-(start+last+1)/2)*pitch
            s=Pos(px,py,-0.08)*Box((x1-x0)*pitch,(last-start+1)*pitch,0.04,align=(Align.CENTER,Align.CENTER,Align.MIN))
            s.label='face_pixel_preview'
            s.color=Color(0.30,0.80,1.0)
            parts.append(s)
            start=last=y
    standing=[Pos(0,0,28.5)*Rot(0,0,180)*Rot(90,0,0)*s for s in parts]
    return Compound(label='Piku the sleepy bunny',children=standing)
