"""Piku matching lid, with two touch-module retaining fingers.
Print exterior down; rear 16 x 14 cable opening is unchanged.
"""
from build123d import *
from piku_lid_base import gen_step as original_back
from piku_mounts import block,TOUCH_END

def gen_step():
    lid=original_back()
    for x in (-4.8,4.8):
        lid+=block(x-0.7,x+0.7,21.0,22.1,1.8,34-(TOUCH_END+0.3))
    lid.label='piku_back_with_touch_retaining_fingers'
    lid.color=Color(0.78,0.69,0.60)
    return lid
