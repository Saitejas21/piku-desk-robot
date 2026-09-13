"""Exterior-only cat sculpture, in the existing raw X/Y/Z assembly frame.

All sections use the original cavity and mounting datums. Forelegs and hocks
are continuous section lofts with distinct ankles, toes and planted soles.
"""
from cat_common import *

def horizontal_section(y,x,z,width,depth):
    return Plane(origin=(x,y,z),x_dir=(1,0,0),z_dir=(0,1,0))*Ellipse(width/2,depth/2)

def section_limb(sections):
    return loft([horizontal_section(*s) for s in sections])

def foreleg():
    # y, x, z, width, depth. The lower paw is broad; the wrist is narrower.
    return section_limb([
        (0,10.4,0.8,14.8,18),
        (2.8,10.4,0.1,18.2,22),
        (7.5,10.7,0.4,17.6,20.5),
        (13,11.2,2.0,11.8,14),
        (23,13.0,6.4,12.4,15),
        (34,14.4,11.6,12.8,16),
        (43,12.5,15,7,10),
    ])

def hind_hock():
    # A low splayed hind foot rises into the folded hip, rather than a capsule.
    return section_limb([
        (0,23.8,13.4,14.5,23),
        (3,24.5,12.8,18.8,27),
        (8,25.0,14.1,20.2,27.2),
        (14,24.5,18.0,18.2,24),
        (22,22.0,22.8,13.0,18),
        (29,18.5,25.0,7.5,12),
    ])

def pear_profile(scale=1):
    # A single seated torso outline: narrower shoulders, outward folded hips.
    points=[(0,50),(13,47),(21,39),(26,29),(29.5,18),(28.5,9),
            (21,3),(0,1),(-21,3),(-28.5,9),(-29.5,18),(-26,29),
            (-21,39),(-13,47)]
    pts=[(x*scale,26+(y-26)*scale) for x,y in points]
    return Face(Wire([Spline(*pts,periodic=True)]))

def seated_torso():
    # Keep the same spline topology at every section to avoid loft twisting.
    return loft([Pos(0,0,z)*pear_profile(s) for z,s in
                 [(1.8,.60),(3.2,.80),(8,.98),(18,1),(30,.97),(39,.72)]])

def feline_head():
    # One continuous broad-cheek skull surface; no separate cheek blobs/muzzle.
    # End below the original crown: coincident tangent crowns create tiny
    # unmeshable slivers. The original crown and touch patch remain intact.
    points=[(0,83.8),(17,80.8),(29,76),(36,65),(37.5,55),(34,44),(24,37),(0,34.5),
            (-24,37),(-34,44),(-37.5,55),(-36,65),(-29,76),(-17,80.8)]
    profiles=[]
    for z,s in [(-1.2,.76),(2,.90),(10,1),(28,1),(39,.90)]:
        pts=[(x*s,60+(y-60)*s) for x,y in points]
        profiles.append(Pos(0,0,z)*Face(Wire([Spline(*pts,periodic=True)])))
    return loft(profiles)

def paw_creases():
    grooves=[]
    for dx in (-3.0,3.0):
        curve=Spline((10.4+dx,2.5,-10.0),(10.4+dx,4.3,-10.6),(10.6+dx,6.2,-9.8))
        grooves.append(sweep(Plane(origin=curve@0,z_dir=curve%0)*Circle(.32),path=curve))
    for dx in (-3,3):
        curve=Spline((24.5+dx,1.2,1.7),(24.5+dx,3.4,-.1),(24.8+dx,6.3,.2))
        grooves.append(sweep(Plane(origin=curve@0,z_dir=curve%0)*Circle(.32),path=curve))
    return grooves
