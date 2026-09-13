"""Seated chibi cat with shaped forelegs, planted paws and a rear-side curl.
Paint suggestions are recessed/raised details in the single printable body.
Raw frame: X width, Y standing height, Z from front to rear.
"""
from functools import lru_cache
from cat_common import *
from cat_exterior import seated_torso,foreleg,hind_hock,feline_head,paw_creases

def display_bezel():
    # An electronic display rim, with no physical muzzle or facial features.
    # The aperture, front datum and all display mounts remain unchanged.
    return rolled(44,27,8,2.4,OLED_Y,-1.2,0.7)

@lru_cache(maxsize=2)
def gen_raw(clips=True):
    body=rolled(HEAD_W,HEAD_H,HEAD_R,REAR,HEAD_Y,0,10)
    body+=rolled(TORSO_W,TORSO_H,TORSO_R,REAR-4,TORSO_Y,4,6)
    envelope=body
    body+=seated_torso()
    # Preserve the original 85 mm outer crown datum above the touch patch.
    body+=feline_head() & block(-60,60,0,85,-20,REAR)
    for side in (-1,1):
        for feature in [ear_shape(),foreleg(),hind_hock()]:
            body+=feature if side==1 else mirror(feature,about=Plane.YZ)
    body+=display_bezel()
    body &= block(-60,60,0,110,-20,REAR)
    body-=cavity()
    body+=face_tunnel()
    body-=face_opening()
    body-=touch_recess()
    for side in (-1,1):
        recess=inner_ear_recess()
        body-=recess if side==1 else mirror(recess,about=Plane.YZ)
        for groove in paw_creases():
            body-=groove if side==1 else mirror(groove,about=Plane.YZ)
        for dy in (-4,0,4):
            body-=ellipsoid(3.2,0.34,0.6,side*26.5,OLED_Y+dy,-1.1,angle=side*dy*2)
    for x,y in SCREWS:
        body+=Pos(x,y,20)*Cylinder(3.4,REAR-20,align=(Align.CENTER,Align.CENTER,Align.MIN))
        body-=Pos(x,y,REAR-8)*Cylinder(0.85,9,align=(Align.CENTER,Align.CENTER,Align.MIN))
    for feature in oled_pads()+touch_rails()+(oled_clips() if clips else []):
        body+=feature
    for rail in tray_rails():body+=rail & envelope
    # Keep decorative tail material outside the electronics cavity.
    body+=tail_shape()-cavity()
    body.label='Piku_cat_body' if clips else 'Piku_cat_body_tape_option'
    body.color=FUR
    return body

def print_location():
    return Pos(0,0,-gen_raw().bounding_box().min.Z)

def gen_step():
    return print_location()*gen_raw()
