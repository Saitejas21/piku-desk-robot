"""Validate exported print meshes and nominal assembly clearance. Python/build123d.
This is geometry validation, not a physical snap-force or electrical test.
"""
import sys,json,struct,collections,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'cad'))
from otter_common import *
from otter_body import gen_raw as body_shape,gen_step as body_print
from otter_back import gen_raw as back_shape,gen_step as back_print
from otter_c3_tray import gen_raw as tray_shape,gen_step as tray_print
from otter_body_tape import gen_step as tape_print
from otter_oled_fit_test import gen_step as oled_test
from otter_touch_fit_test import gen_step as touch_test

def overlap(a,b):
    common=a & b
    return sum(s.volume for s in common.solids()) if common is not None else 0

def mesh_check(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n, path
    edges=collections.Counter();directions=collections.Counter();volume=0
    for i in range(n):
        values=struct.unpack_from('<12fH',data,84+50*i)
        vertices=[tuple(round(k,5) for k in values[3+j*3:6+j*3]) for j in range(3)]
        for a,b in zip(vertices,vertices[1:]+vertices[:1]):
            edges[tuple(sorted((a,b)))]+=1;directions[(a,b)]+=1
        a,b,c=vertices
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    nonmanifold=sum(c!=2 for c in edges.values())
    inconsistent=sum(directions[(a,b)]!=directions[(b,a)] for a,b in edges)
    assert nonmanifold==0 and inconsistent==0 and volume>0,(path,nonmanifold,inconsistent,volume)
    return {'triangles':n,'boundary_or_nonmanifold_edges':nonmanifold,'inconsistent_winding':inconsistent,
            'signed_volume_mm3':round(volume,3),'sha256':hashlib.sha256(data).hexdigest()}

report={'physical_fit_tested':False,'clip_force_or_life_tested':False,'battery_and_charger_fitted':False,
        'dimensions_note':'Nominal footprints; PCB thickness, glass alignment, socket and header envelopes require measurement.',
        'parts':{}}
body,back,tray=body_shape(),back_shape(),tray_shape()
for name,shape in [('otter_body',body_print()),('otter_back',back_print()),('otter_c3_tray',tray_print()),
                   ('otter_body_tape',tape_print()),('otter_oled_fit_test',oled_test()),('otter_touch_fit_test',touch_test())]:
    assert shape.is_valid and len(shape.solids())==1 and shape.volume>0,(name,shape.is_valid,len(shape.solids()))
    b=shape.bounding_box();assert abs(b.min.Z)<1e-4,(name,b.min.Z)
    report['parts'][name]={'valid':True,'solids':1,'bbox_mm':list(b.size),'print_min_z_mm':b.min.Z,
        'volume_mm3':shape.volume,'stl':mesh_check(root/'cad'/f'{name}.stl')}
print('Print solid and mesh checks passed.',flush=True)
modules=nominal_oled()+nominal_touch()+nominal_c3()
parts=[body,back,tray]+modules
collisions=[]
for i,a in enumerate(parts):
    for j,b in enumerate(parts[i+1:],i+1):
        v=overlap(a,b)
        if v>1e-5:collisions.append([i,a.label,j,b.label,v])
report['assembled_part_collisions']=collisions
assert not collisions,collisions
report['overall_raw_bbox_mm']=list(Compound(children=[body,back]).bounding_box().size)
report['closed_main_body_depth_without_tail_mm']=49+LID_T
report['usb_plug_vs_shell_overlap_mm3']=overlap(usb_plug_envelope(),body)+overlap(usb_plug_envelope(),back)
assert report['usb_plug_vs_shell_overlap_mm3']<1e-5
report['wire_corridors_vs_parts_mm3']=[sum(overlap(c,p) for p in parts) for c in wire_corridors()]
assert max(report['wire_corridors_vs_parts_mm3'])<1e-5

# Nominal module pieces are axis-aligned boxes: this is an exact translational
# sweep, not a sample of a few positions along the insertion path.
def box_sweep(shape,dz):
    b=shape.bounding_box()
    return block(b.min.X,b.max.X,b.min.Y,b.max.Y,b.min.Z,b.max.Z+dz)

rigid_body=body
for c in oled_clips():rigid_body-=c
oled_sweeps=[box_sweep(p,65) for p in nominal_oled()]
report['OLED_insertion_except_compliant_clips_mm3']=sum(overlap(s,rigid_body) for s in oled_sweeps)
assert report['OLED_insertion_except_compliant_clips_mm3']<1e-5
touch_sweeps=[box_sweep(p,50) for p in nominal_touch()]
report['touch_insertion_mm3']=sum(overlap(s,p) for s in touch_sweeps for p in [body,tray]+nominal_oled()+nominal_c3())
assert report['touch_insertion_mm3']<1e-5
# Conservative tray sweep fills its cutouts and includes its pad heights.
tb=tray.bounding_box()
tray_sweeps=[block(tb.min.X,tb.max.X,TRAY_Y,TRAY_Y+TRAY_T,TRAY_FRONT,TRAY_REAR+50)]
for x in (-7,7):
    for z in C3_PAD_Z:
        tray_sweeps.append(block(x-1.4,x+1.4,TRAY_Y+TRAY_T,C3_Y-0.4,z-0.6,z+0.6+50))
tray_sweeps += [box_sweep(p,50) for p in nominal_c3()]
report['C3_loaded_tray_insertion_mm3']=sum(overlap(s,p) for s in tray_sweeps for p in [body]+nominal_oled()+nominal_touch())
assert report['C3_loaded_tray_insertion_mm3']<1e-5,report['C3_loaded_tray_insertion_mm3']
print('Nominal fit and straight insertion paths passed.',flush=True)

# Check complete nominal lit rectangle remains unobstructed for selected views.
view_checks=[]
z_near=OLED_FRONT-2.96;z_far=-12
for yaw,pitch in [(0,0),(-25,0),(25,0),(0,-15),(0,15)]:
    run=z_near-z_far
    near=Pos(0,OLED_Y,z_near)*Rectangle(21.74,10.87)
    far=Pos(run*math.tan(math.radians(yaw)),OLED_Y+run*math.tan(math.radians(pitch)),z_far)*Rectangle(21.74,10.87)
    beam=loft([near,far]);v=overlap(beam,body)
    view_checks.append({'horizontal_deg':yaw,'vertical_deg':pitch,'shell_obstruction_mm3':v})
    assert v<1e-5,view_checks[-1]
report['nominal_active_display_visibility']=view_checks
report['cavity_connected_solids']=len(cavity().solids());assert report['cavity_connected_solids']==1
report['interfaces_mm']={'head_wall':WALL,'crown_wall_centre':0.8,'touch_roof_gap':0.15,
    'OLED_side_clearance':OLED_SIDE_GAP,'OLED_axial_clearance':OLED_AXIAL_GAP,'OLED_clip_overlap':CLIP_OVERLAP,
    'touch_slot_total_clearance':TOUCH_SLOT-TOUCH_T,'tray_side_clearance':0.3,'tray_slot_total_clearance':0.3,
    'lid_lip_side_clearance':0.3,'touch_rear_stop_clearance':0.3,'tray_rear_stop_clearance':0.3,
    'USB_opening':[16,14],'nominal_USB_plug_cross_section':[13,6]}
report['screw_centres_xy_mm']=SCREWS
# Coaxial clearance and pilot paths share the same named SCREWS list.
report['screws']={'count':4,'pilot_diameter_mm':1.7,'lid_clearance_diameter_mm':2.4,'suggested':'M2 x 6 mm self-tapping'}
report['reserve_space']={'envelope_mm':[24,6,20],'selected_battery':False}
reserve=block(-12,12,32,38,20,40)
report['reserve_space']['overlap_with_parts_or_wire_lanes_mm3']=sum(overlap(reserve,p) for p in parts+wire_corridors())
assert report['reserve_space']['overlap_with_parts_or_wire_lanes_mm3']<1e-5
(root/'cad/validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'result':'passed','overall_mm':report['overall_raw_bbox_mm'],'parts':list(report['parts']),
                  'physical_fit_tested':False,'battery_and_charger_fitted':False},indent=2))
