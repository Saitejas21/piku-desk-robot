"""Piku prototype: rear push-in OLED clips and sliding crown touch rails.
Print face down, rear open upwards; PETG; test coupons before the whole body.
"""
from build123d import *
from piku_shell_base import gen_step as original_body
from piku_mounts import *

def gen_step():
    body=original_body()-touch_recess()
    for feature in oled_supports()+oled_clips()+touch_rails():
        body+=feature
    body.label='piku_body_with_PCB_clips_and_touch_rails'
    body.color=Color(0.94,0.86,0.76)
    return body
