"""Smooth seated otter shell. Raised cream areas are paintable geometry.
gen_raw() uses assembly coordinates; gen_step() puts frontmost points on bed.
"""
from functools import lru_cache
from otter_common import *

def muzzle_shape():
    return rolled(44,27,13,2.4,OLED_Y,-1.2,0.7)

def belly_shape():
    shape=Pos(0,26,2.5)*extrude(Ellipse(13,17),amount=3)
    edges=[e for e in shape.edges() if abs(e.center().Z-2.5)<1e-6]
    return fillet(edges,0.65)

@lru_cache(maxsize=2)
def gen_raw(clips=True):
    body=rolled(HEAD_W,HEAD_H,HEAD_R,REAR,HEAD_Y,0,10)
    body+=rolled(TORSO_W,TORSO_H,TORSO_R,REAR-4,TORSO_Y,4,6)
    envelope=body
    # Small circular ears and short relaxed forepaws preserve the otter silhouette.
    for side in (-1,1):
        body+=ellipsoid(6,6,6,side*29.5,77.5,13)
        body+=ellipsoid(7,15,8,side*15.5,31,2,angle=-side*20)
        body+=ellipsoid(6.5,7,7,side*10.5,20.5,1)
        body+=ellipsoid(12,10,18,side*15.5,7.5,11)
    body+=muzzle_shape()
    body+=belly_shape()
    body &= block(-60,60,0,100,-20,REAR)
    body-=cavity()
    body+=face_tunnel()
    body-=face_opening()
    body-=touch_recess()
    # Paint recesses in the ears; shallow toe lines read as paws without texture.
    for side in (-1,1):
        body-=ellipsoid(3.2,3.2,1.8,side*29.5,77.5,6.7)
        for dx in (-2.6,2.6):
            body-=ellipsoid(0.45,2.5,0.9,side*15.5+dx,7.5,-6.8)
    for x,y in SCREWS:
        body+=Pos(x,y,20)*Cylinder(3.4,REAR-20,align=(Align.CENTER,Align.CENTER,Align.MIN))
        body-=Pos(x,y,REAR-8)*Cylinder(0.85,9,align=(Align.CENTER,Align.CENTER,Align.MIN))
    for feature in oled_pads()+touch_rails()+(oled_clips() if clips else []):
        body+=feature
    # Clip each rail before adding it so decorative feet remain untouched.
    for rail in tray_rails():body+=rail & envelope
    body+=tail_shape()
    body.label='Piku_otter_body' if clips else 'Piku_otter_body_tape_option'
    body.color=BROWN
    return body

def print_location():
    return Pos(0,0,-gen_raw().bounding_box().min.Z)

def gen_step():
    return print_location()*gen_raw()
