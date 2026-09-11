import sys,json,struct,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'cad'
sys.path.insert(0,str(root))
from build123d import *
from piku_body import gen_step as body_shape
from piku_back import gen_step as back_shape
from piku_shell_base import gen_step as base_shape
from piku_mounts import *
from piku_oled_fit_test import gen_step as oled_coupon
from piku_touch_fit_test import gen_step as touch_coupon

def overlap(a,b):
    c=a & b
    return sum(s.volume for s in c.solids()) if c is not None else 0

def check_mesh(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n
    edges=collections.Counter();directions=collections.Counter();volume=0
    for i in range(n):
        f=struct.unpack_from('<12fH',data,84+50*i)
        v=[tuple(round(k,4) for k in f[3+j*3:6+j*3]) for j in range(3)]
        for a,b in zip(v,v[1:]+v[:1]):
            edges[tuple(sorted((a,b)))]+=1;directions[(a,b)]+=1
        a,b,c=v
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    bad=sum(v!=2 for v in edges.values())
    wrong=sum(directions[(a,b)]!=directions[(b,a)] for a,b in edges)
    assert bad==0 and wrong==0 and volume>0,(path,bad,wrong,volume)
    return dict(triangles=n,boundary_or_nonmanifold_edges=bad,inconsistent_winding=wrong)

out={'physical_fit_tested':False,'snap_force_or_strength_tested':False,
     'module_geometry':'nominal listed footprint; PCB thickness, glass, headers and component extents assumed',
     'battery_pack_fit_or_electrical_design_validated':False}
body,back=body_shape(),back_shape()
closed_back=Pos(0,0,34)*Rot(0,180,0)*back
for name,shape in [('piku_body',body),('piku_back',back),
                   ('piku_oled_fit_test',oled_coupon()),('piku_touch_fit_test',touch_coupon())]:
    out[name]={'valid':shape.is_valid,'solids':len(shape.solids()),'bbox_mm':list(shape.bounding_box().size),'volume_mm3':shape.volume}
    assert shape.is_valid and len(shape.solids())==1 and shape.volume>0,out[name]
    if (root/(name+'.stl')).exists():out[name]['mesh']=check_mesh(root/(name+'.stl'))
out['body_lid_overlap_mm3']=overlap(body,closed_back)
assert out['body_lid_overlap_mm3']<1e-5,out['body_lid_overlap_mm3']
modules=nominal_oled()+nominal_touch()
out['seated_module_collisions_mm3']={}
for mod in modules:
    value=overlap(body,mod)+overlap(closed_back,mod)
    out['seated_module_collisions_mm3'][mod.label]=value
    assert value<1e-5,(mod.label,value)
out['module_pair_overlap_mm3']=sum(overlap(a,b) for i,a in enumerate(modules) for b in modules[i+1:])
assert out['module_pair_overlap_mm3']<1e-5
# All modeled module pieces are axis-aligned boxes. Swept AABBs are therefore
# the exact solid union over straight +Z insertion travel, not sparse samples.
def swept_box(shape,travel):
    b=shape.bounding_box()
    return block(b.min.X,b.max.X,b.min.Y,b.max.Y,b.min.Z,b.max.Z+travel)
touch_sweeps=[swept_box(m,30) for m in nominal_touch()]
out['touch_insertion_sweep_collisions_mm3']=sum(overlap(s,body) for s in touch_sweeps)
out['touch_insertion_vs_installed_OLED_mm3']=sum(overlap(s,o) for s in touch_sweeps for o in nominal_oled())
assert out['touch_insertion_sweep_collisions_mm3']<1e-5
assert out['touch_insertion_vs_installed_OLED_mm3']<1e-5
# Remove only intended compliant clips for insertion clearance check.
rigid=body
for clip in oled_clips():rigid-=clip
oled_sweeps=[swept_box(m,40) for m in nominal_oled()]
out['oled_insertion_rigid_collisions_mm3']=sum(overlap(s,rigid) for s in oled_sweeps)
assert out['oled_insertion_rigid_collisions_mm3']<1e-5,out['oled_insertion_rigid_collisions_mm3']
out['clearances_mm']={'OLED_side':OLED_SIDE_GAP,'OLED_axial':OLED_AXIAL_GAP,
    'OLED_latch_overlap':CLIP_OVERLAP,'touch_side':TOUCH_SIDE_GAP,
    'touch_thickness_total':TOUCH_SLOT-TOUCH_T,'touch_roof_nominal_gap':TOUCH_ROOF-(TOUCH_BACK_Y+TOUCH_T),
    'touch_lid_end_clearance':0.3,'crown_centre_wall':0.8}
base=base_shape()
out['exterior_bbox_unchanged']=all(abs(a-b)<1e-6 for a,b in zip(body.bounding_box().size,base.bounding_box().size))
assert out['exterior_bbox_unchanged']
(root/'validation.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
