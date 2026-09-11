"""Open-back assembly. Blue/red boards are NOMINAL fit envelopes only."""
from build123d import *
from piku_body import gen_step as body_shape
from piku_mounts import nominal_oled,nominal_touch

def gen_step():
    parts=[body_shape()]+nominal_oled()+nominal_touch()
    return Compound(label='Piku_open_back_nominal_module_fit',children=parts)
