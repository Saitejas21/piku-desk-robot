"""Open back: all three nominal boards, removable C3 tray and module mounts."""
from cat_common import *
from cat_assembly import raw_parts

def gen_step():
    return Compound(label='Piku_cat_nominal_internal_layout',children=raw_parts(False,False))
