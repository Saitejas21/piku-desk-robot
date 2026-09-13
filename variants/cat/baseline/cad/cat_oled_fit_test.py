"""Small flat OLED clip coupon; same interface as the cat face."""
from cat_common import *

def gen_step():
    test=rounded(35,34,2,WALL+1.2,OLED_Y,-1.2)
    test+=face_tunnel()
    test-=face_opening()
    for p in oled_pads()+oled_clips():test+=p
    test=Pos(0,-OLED_Y,1.2)*test
    test.label='Cat_OLED_fit_test'
    return test
