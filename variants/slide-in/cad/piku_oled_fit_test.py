"""Small OLED fit coupon; same front datum and clips as Piku body."""
from build123d import *
from piku_mounts import *

def gen_step():
    coupon=extrude(RectangleRounded(35,34,2),amount=3)
    coupon=Pos(0,OLED_Y,0)*coupon
    coupon-=Pos(0,OLED_Y,-1)*extrude(RectangleRounded(25,16,3),amount=5)
    for feature in oled_supports()+oled_clips():
        coupon+=feature
    coupon.label='OLED_fit_coupon_print_face_down'
    return coupon
