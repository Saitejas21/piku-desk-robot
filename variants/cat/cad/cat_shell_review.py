"""Standing cat with the OLED off for unpainted silhouette review."""
from cat_common import STAND,Compound
from cat_assembly import raw_parts

def gen_step():
    return Compound(label='Piku_cat_OLED_off_review',
                    children=[STAND*p for p in raw_parts(True,False)])
