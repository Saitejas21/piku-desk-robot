"""Crown pocket coupon; same rails and 0.8 mm central roof thickness."""
from build123d import *
from piku_body import gen_step as body_shape
from piku_mounts import block

def gen_step():
    coupon=body_shape() & block(-9.2,9.2,19.6,23.1,11.0,32.0)
    # Put the outer crown on the print bed. Curved ends remain above it.
    coupon=Rot(-90,0,0)*coupon
    bb=coupon.bounding_box()
    coupon=Pos(0,-(bb.min.Y+bb.max.Y)/2,-bb.min.Z)*coupon
    coupon.label='TTP223_fit_coupon_print_roof_down'
    return coupon
