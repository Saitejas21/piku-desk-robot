"""Piku cat parameters, mm. Raw X=width, Y=height, +Z=front to rear.

Board footprints are nominal. PCB thickness and component/header envelopes
are assumptions to check against received hardware before printing.
"""
from build123d import *

HEAD_W, HEAD_H, HEAD_Y, HEAD_R = 70.0,50.0,60.0,24.0
TORSO_W,TORSO_H,TORSO_Y,TORSO_R = 49.0,48.0,26.0,23.0
REAR, LID_T, WALL = 42.0,2.0,2.4
OLED_Y, OLED_FRONT, OLED_W, OLED_H, OLED_T = 60.0,8.5,27.0,27.0,1.2
OLED_SIDE_GAP, OLED_AXIAL_GAP, CLIP_T, CLIP_OVERLAP = 0.25,0.25,0.8,0.4
TOUCH_W,TOUCH_L,TOUCH_T = 11.0,15.0,1.0
TOUCH_ROOF,TOUCH_START,TOUCH_SLOT = 84.2,18.0,1.3
TOUCH_END=TOUCH_START+TOUCH_L
TOUCH_BACK_Y=TOUCH_ROOF-(TOUCH_SLOT+TOUCH_T)/2
TRAY_W,TRAY_FRONT,TRAY_REAR,TRAY_Y,TRAY_T = 28.0,13.0,41.2,13.0,1.6
C3_W,C3_L,C3_T = 18.0,22.5,1.6
C3_FRONT,C3_Y=19.0,17.0
C3_PAD_Z=(C3_FRONT+0.7,C3_FRONT+C3_L-1.0)
SCREWS=[(-29.8,64.0),(29.8,64.0),(-19.5,15.0),(19.5,15.0)]
FUR=Color(0.43,0.46,0.49)
CHEST=Color(0.82,0.84,0.85)
STAND=Rot(0,0,180)*Rot(90,0,0)

def block(x0,x1,y0,y1,z0,z1):
    return Pos(x0,y0,z0)*Box(x1-x0,y1-y0,z1-z0,align=(Align.MIN,Align.MIN,Align.MIN))

def rounded(w,h,r,depth,y=0,z=0,x=0):
    return Pos(x,y,z)*extrude(RectangleRounded(w,h,r),amount=depth)

def rolled(w,h,r,depth,y,z,roll):
    shape=rounded(w,h,r,depth,y,z)
    edges=[e for e in shape.edges() if abs(e.bounding_box().min.Z-z)<1e-6 and abs(e.bounding_box().max.Z-z)<1e-6]
    return fillet(edges,roll)

def ellipsoid(rx,ry,rz,x,y,z,angle=0):
    shape=Sphere(1).scale((rx,ry,rz))
    # Microscopic planar caps avoid zero-area STL triangles at spline poles.
    # 0.01 mm is well below the intended 0.2 mm printing layer height.
    shape &= block(-rx-1,rx+1,-ry-1,ry+1,-rz+0.01,rz-0.01)
    return Pos(x,y,z)*Rot(0,0,angle)*shape

def back_profile(inset=0):
    head=Pos(0,HEAD_Y)*RectangleRounded(HEAD_W-2*inset,HEAD_H-2*inset,HEAD_R-inset)
    torso=Pos(0,TORSO_Y)*RectangleRounded(TORSO_W-2*inset,TORSO_H-2*inset,TORSO_R-inset)
    return head+torso

def cavity():
    head=rolled(HEAD_W-2*WALL,HEAD_H-2*WALL,HEAD_R-WALL,REAR+2-WALL,HEAD_Y,WALL,10-WALL)
    torso=rolled(TORSO_W-2*WALL,TORSO_H-2*WALL,TORSO_R-WALL,REAR+2-7.5,TORSO_Y,7.5,3.5)
    return head+torso

def tail_shape(clearance=0):
    # The broad hook sits toward the rear, outside the lid and USB paths.
    # Circular curvature is larger than the tube radius everywhere, avoiding
    # an inward spline fold. Tilt the curl so it also reads from the side.
    # The starting cap is fully buried in the haunch, with no exposed cut end.
    path=Pos(33,21,31.5)*Rot(0,-30,0)*CenterArc((0,0),11,-175,285)
    radius=4.2+clearance
    profile=Plane(origin=path@0,z_dir=path%0)*Circle(radius)
    tail=sweep(profile,path=path)
    tip=path@1
    cap_r=radius+0.2
    # Trim 0.01 mm at the sphere poles to avoid zero-area STL triangles.
    cap=Sphere(cap_r) & block(-cap_r-1,cap_r+1,-cap_r-1,cap_r+1,-cap_r+0.01,cap_r-0.01)
    tail+=Pos(tip.X,tip.Y,tip.Z)*cap
    return tail

def ear_profile(inner=False):
    # Deliberately pointed feline ears, with softly rounded tips.
    pts=[(13,76),(35,75),(30,101)] if not inner else [(19,79),(30.5,78.7),(28.9,94.5)]
    profile=Polygon(*pts,align=None)
    return fillet(profile.vertices(),2.3 if not inner else 1.2)

def ear_shape():
    # Broad root blends into the skull; both width and depth taper to the tip.
    sections=[]
    for y,x,z,w,d in [(71,24,14.5,23,24),(80,26,12,19,18),
                      (90,28,10.5,11.5,11),(97,29,9.5,3.5,3.8),
                      (98.3,29.1,9.4,.9,1.1)]:
        sections.append(Plane(origin=(x,y,z),x_dir=(1,0,0),z_dir=(0,1,0))*Ellipse(w/2,d/2))
    return loft(sections)

def inner_ear_recess():
    return Pos(0,0,-4)*extrude(ear_profile(True),amount=11.4)

def face_opening():
    # Flared opening preserves a useful viewing angle for the recessed glass.
    mouth=Pos(0,OLED_Y,-2)*RectangleRounded(33,23,5)
    throat=Pos(0,OLED_Y,5.5)*RectangleRounded(25,16,3)
    return loft([mouth,throat])+rounded(25,16,3,12,OLED_Y,5.4)

def face_tunnel():
    # An internal shroud reaches nearly to the glass and conceals PCB edges.
    front=Pos(0,OLED_Y,1.7)*RectangleRounded(34,24,6)
    rear=Pos(0,OLED_Y,5.5)*RectangleRounded(29,20,4)
    return loft([front,rear])

def oled_pads():
    return [block(x-0.75,x+0.75,OLED_Y+dy-1.4,OLED_Y+dy+1.4,2.2,OLED_FRONT)
            for x in (-12.75,12.75) for dy in (-11.5,11.5)]

def oled_clips():
    clips=[];edge=OLED_W/2;inner=edge+OLED_SIDE_GAP
    catch=OLED_FRONT+OLED_T+OLED_AXIAL_GAP
    for dy in (-11.5,11.5):
        y=OLED_Y+dy
        beam=block(inner,inner+CLIP_T,y-1.5,y+1.5,2.2,catch+1.2)
        ramp_profile=Plane.XZ*Polygon((edge-CLIP_OVERLAP,catch),(inner+CLIP_T,catch),
                                     (inner+CLIP_T,catch+1.2),(inner,catch+1.2),align=None)
        beam+=Pos(0,y+1.5,0)*extrude(ramp_profile,amount=3)
        beam+=block(inner,inner+1.6,y-2,y+2,2.2,3.5)
        clips.extend([beam,mirror(beam,about=Plane.YZ)])
    return clips

def touch_recess():
    return block(-9,9,82.0,TOUCH_ROOF,16.0,REAR+1)

def touch_rails():
    out=[];edge=TOUCH_W/2;inner=edge+0.25;bottom=TOUCH_ROOF-TOUCH_SLOT
    for side in (-1,1):
        rail=block(inner,8,81.7,84.5,16.8,38.8)
        rail+=block(edge-0.8,inner+0.1,81.7,bottom,16.8,38.8)
        rail+=block(edge-0.8,inner+0.1,bottom,84.3,16.8,TOUCH_START)
        out.append(rail if side==1 else mirror(rail,about=Plane.YZ))
    return out

def tray_rails():
    # Rails grip the removable plastic tray; they do not squeeze the C3 PCB.
    out=[];edge=TRAY_W/2
    for s in (-1,1):
        rail=block(edge+0.3,25,TRAY_Y-1.2,TRAY_Y+TRAY_T+1.5,12,38.8)
        rail-=block(edge-1,edge+0.3,TRAY_Y,TRAY_Y+TRAY_T+0.3,11,40)
        rail+=block(edge-1.2,edge+0.35,TRAY_Y-1.2,TRAY_Y,12,38.8)
        rail+=block(edge-1.2,edge+0.35,TRAY_Y+TRAY_T+0.3,TRAY_Y+TRAY_T+1.5,12,38.8)
        # Stop at the forward end, while leaving the tray clear of the front wall.
        rail+=block(edge-1.2,edge+0.35,TRAY_Y,TRAY_Y+TRAY_T+0.3,12,TRAY_FRONT)
        out.append(rail if s==1 else mirror(rail,about=Plane.YZ))
    return out

def nominal_oled():
    pcb=block(-OLED_W/2,OLED_W/2,OLED_Y-OLED_H/2,OLED_Y+OLED_H/2,OLED_FRONT,OLED_FRONT+OLED_T)
    pcb.label='OLED_PCB_nominal_27x27x1p2';pcb.color=Color(0.08,0.30,0.60)
    glass=block(-13.25,13.25,OLED_Y-9.7,OLED_Y+9.7,OLED_FRONT-2.9,OLED_FRONT)
    glass.label='OLED_glass_nominal';glass.color=Color(0.025,0.04,0.045)
    header=block(-5.2,5.2,OLED_Y+10.5,OLED_Y+13,OLED_FRONT+OLED_T,OLED_FRONT+OLED_T+8)
    header.label='OLED_header_keepout';header.color=Color(0.25,0.26,0.27)
    return [pcb,glass,header]

def nominal_touch():
    pcb=block(-TOUCH_W/2,TOUCH_W/2,TOUCH_BACK_Y,TOUCH_BACK_Y+TOUCH_T,TOUCH_START,TOUCH_END)
    pcb.label='TTP223_PCB_nominal_11x15x1';pcb.color=Color(0.70,0.08,0.10)
    chip=block(-2,2,TOUCH_BACK_Y-1.3,TOUCH_BACK_Y,TOUCH_START+4,TOUCH_START+7)
    chip.label='TTP223_chip_keepout';chip.color=Color(0.15,0.16,0.17)
    header=block(-3.8,3.8,TOUCH_BACK_Y-8,TOUCH_BACK_Y,TOUCH_END-2.8,TOUCH_END-0.3)
    header.label='TTP223_header_keepout';header.color=Color(0.25,0.26,0.27)
    return [pcb,chip,header]

def nominal_c3():
    pcb=block(-C3_W/2,C3_W/2,C3_Y,C3_Y+C3_T,C3_FRONT,C3_FRONT+C3_L)
    pcb.label='C3_SuperMini_nominal_18x22p5x1p6';pcb.color=Color(0.10,0.35,0.35)
    usb=block(-4.6,4.6,C3_Y+C3_T,C3_Y+C3_T+3.3,36.6,42.2)
    usb.label='C3_USB_C_socket_nominal';usb.color=Color(0.63,0.66,0.68)
    chip=block(-4.5,4.5,C3_Y+C3_T,C3_Y+C3_T+2,24,32)
    chip.label='C3_components_keepout';chip.color=Color(0.16,0.17,0.18)
    headers=[]
    for x in (-7.62,7.62):
        h=block(x-1.27,x+1.27,C3_Y+C3_T,C3_Y+C3_T+10,C3_FRONT+2,C3_FRONT+C3_L-2)
        h.label='C3_header_and_jumper_keepout';h.color=Color(0.27,0.28,0.29)
        headers.append(h)
        pins=block(x-0.4,x+0.4,C3_Y-2.2,C3_Y,C3_FRONT+2,C3_FRONT+C3_L-2)
        pins.label='C3_solder_tail_keepout_2p2_mm';pins.color=Color(0.63,0.66,0.68)
        headers.append(pins)
    return [pcb,usb,chip]+headers

def usb_plug_envelope():
    return block(-6.5,6.5,17.3,23.3,42.2,65)

def wire_corridors():
    # Reserved routing lanes, separate from actual modeled hardware.
    return [block(13,17,31,76,21,25),block(-4,17,72,76,21,25)]
