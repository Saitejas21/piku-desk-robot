"""Open back: all three nominal boards, removable C3 tray and module mounts."""
from otter_common import *
from otter_assembly import raw_parts

def gen_step():
    return Compound(label='Piku_otter_nominal_internal_layout',children=raw_parts(False,False))
