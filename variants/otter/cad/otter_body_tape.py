"""Optional alternate body with corner pads but without OLED snap tabs."""
from otter_body import gen_raw,print_location

def gen_step():
    return print_location()*gen_raw(clips=False)
