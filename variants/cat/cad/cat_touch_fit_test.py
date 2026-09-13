"""Crown rail coupon, outer sensing surface on print bed."""
from cat_common import *

def gen_step():
    test=block(-9.2,9.2,TOUCH_ROOF,85,16,42)
    for rail in touch_rails():test+=rail
    test=Rot(-90,0,0)*test
    b=test.bounding_box()
    test=Pos(0,-(b.min.Y+b.max.Y)/2,-b.min.Z)*test
    test.label='Cat_touch_rail_fit_test'
    return test
