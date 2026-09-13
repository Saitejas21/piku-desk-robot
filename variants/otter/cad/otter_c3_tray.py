"""Sliding insulating C3 tray. Secure PCB on the pads with thin insulating tape.
Printed flat. External rails retain the tray; PCB position remains adjustable.
"""
from functools import lru_cache
from otter_common import *

@lru_cache(maxsize=1)
def gen_raw():
    tray=block(-TRAY_W/2,TRAY_W/2,TRAY_Y,TRAY_Y+TRAY_T,TRAY_FRONT,TRAY_REAR)
    # Keep pin ends above the tray, with a 0.4 mm insulating-pad allowance.
    for x in (-7,7):
        for z in C3_PAD_Z:
            tray+=block(x-1.4,x+1.4,TRAY_Y+TRAY_T,C3_Y-0.4,z-0.6,z+0.6)
    # Cable-tie slots offer optional secondary retention, clear of rail margins.
    for x in (-10.8,10.8):
        tray-=block(x-0.8,x+0.8,TRAY_Y-1,TRAY_Y+TRAY_T+1,24,28)
    tray.label='C3_removable_tray';tray.color=Color(0.76,0.65,0.48)
    return tray

def print_location():
    # +Y thickness becomes +Z; the flat tray bottom is the print datum.
    return Pos(0,27,-TRAY_Y)*Rot(90,0,0)

def gen_step():
    return print_location()*gen_raw()
