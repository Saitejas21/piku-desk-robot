"""Rear cover with tail-clearance notch. Prints flat exterior down."""
from functools import lru_cache
from otter_common import *

@lru_cache(maxsize=1)
def gen_raw():
    lid=Pos(0,0,REAR)*extrude(back_profile(),amount=LID_T)
    lip=back_profile(WALL+0.3)-back_profile(WALL+1.8)
    lid+=Pos(0,0,REAR-2.5)*extrude(lip,amount=2.7)
    lid-=tail_shape(0.3)
    for x,y in SCREWS:
        lid-=Pos(x,y,REAR-4)*Cylinder(1.2,8,align=(Align.CENTER,Align.CENTER,Align.MIN))
        lid-=Pos(x,y,REAR-3)*Cylinder(3.65,3,align=(Align.CENTER,Align.CENTER,Align.MIN))
    # Central USB access, deliberately larger than the nominal connector/plug.
    lid-=rounded(16,14,2,10,20.3,REAR-4)
    for x in (-4.8,4.8):
        lid+=block(x-0.7,x+0.7,83.0,84.1,TOUCH_END+0.3,REAR+0.2)
    for x in (-12.8,12.8):
        lid+=block(x-0.7,x+0.7,13.0,14.6,TRAY_REAR+0.3,REAR+0.2)
    for x in (-18,18):
        lid-=rounded(2,10,0.9,8,54,REAR-3,x)
    lid.label='Piku_otter_back';lid.color=BROWN
    return lid

def print_location():
    # Rear exterior is the bed datum; all locating fingers build upwards.
    return Pos(0,0,REAR+LID_T)*Rot(180,0,0)

def gen_step():
    return print_location()*gen_raw()
