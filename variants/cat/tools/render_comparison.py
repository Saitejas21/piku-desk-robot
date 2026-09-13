"""Render actual current/proposed CAD at identical camera and scale.

VTK material masks simulate paint only; they never alter exported geometry.
The OLED image comes from the existing firmware pixel data in both models.
"""
from pathlib import Path
import sys,types,json,argparse
import vtk
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.TopAbs import TopAbs_REVERSED

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'cad'))
from cat_assembly import raw_parts as proposed_parts
baseline=root/'baseline/cad'

def load_baseline(name):
    alias=name+'_baseline'
    mod=types.ModuleType(alias);mod.__file__=str(baseline/(name+'.py'));sys.modules[alias]=mod
    source=Path(mod.__file__).read_text()
    for n in ['cat_common','cat_exterior','cat_body','cat_back','cat_c3_tray']:
        source=source.replace('from '+n+' import','from '+n+'_baseline import')
    exec(compile(source,mod.__file__,'exec'),mod.__dict__)
    return mod

for n in ['cat_common','cat_exterior','cat_body','cat_back','cat_c3_tray']:load_baseline(n)
current_parts=load_baseline('cat_assembly').raw_parts

def paint_shader(actor,proposed):
    shader=actor.GetShaderProperty()
    shader.AddVertexShaderReplacement('//VTK::PositionVC::Dec',True,
        '//VTK::PositionVC::Dec\nout vec3 paintPosition;\nout vec3 paintNormal;\n',False)
    shader.AddVertexShaderReplacement('//VTK::PositionVC::Impl',True,
        '//VTK::PositionVC::Impl\npaintPosition=vertexMC.xyz;\npaintNormal=normalMC;\n',False)
    shader.AddFragmentShaderReplacement('//VTK::PositionVC::Dec',True,
        '//VTK::PositionVC::Dec\nin vec3 paintPosition;\nin vec3 paintNormal;\n',False)
    face_w,face_h=(28.0,18.8) if proposed else (30.0,20.3)
    chest_scale=1.065 if proposed else 1
    code=f'''
//VTK::Color::Impl
float x=-paintPosition.x;
float y=paintPosition.z;
float z=paintPosition.y;
vec3 coat=vec3(0.54,0.56,0.59);
vec3 ivory=vec3(0.91,0.865,0.765);
float face=pow(abs(x)/{face_w},3.0)+pow(abs(y-60.0)/{face_h},3.0);
if(face<1.0 && z<7.0 && y>36.0)coat=ivory;
float chest=pow(x/10.8,2.0)+pow((y-{29*chest_scale})/{18.4*chest_scale},2.0);
if(chest<1.0 && z<5.0 && z>0.8 && y<{44*chest_scale})coat=ivory;
if(y<10.5 && z<26.5)coat=ivory;
if(abs(z-7.4)<0.02 && abs(paintNormal.y)>0.9999 && y>77.5 && abs(x)>17.5)coat=vec3(0.83,0.51,0.54);
ambientColor=ambientIntensity*coat;
diffuseColor=diffuseIntensity*coat;
'''
    shader.AddFragmentShaderReplacement('//VTK::Color::Impl',True,code,False)

def add_shape(renderer,shape,painted,proposed):
    label=shape.label;col=(.63,.65,.66);emission=False
    if 'glass' in label:col=(.014,.020,.023)
    elif 'pixel' in label:col=(.48,.88,1);emission=True
    elif label.startswith('OLED_PCB'):col=(.06,.22,.32)
    elif label.startswith('TTP223_PCB'):col=(.55,.1,.11)
    elif label.startswith('C3_SuperMini'):col=(.10,.30,.29)
    elif 'USB' in label:col=(.54,.55,.55)
    if painted and label in ['Piku_cat_body','Piku_cat_back']:col=(.54,.56,.59)
    for tolerance in [.035,.010,.002]:
        BRepTools.Clean_s(shape.wrapped)
        BRepMesh_IncrementalMesh(shape.wrapped,tolerance,False,.10,True).Perform()
        if all(BRep_Tool.Triangulation_s(f.wrapped,TopLoc_Location()) is not None for f in shape.faces()):break
    vertices,triangles=shape.tessellate(tolerance,.10)
    normals=vtk.vtkFloatArray();normals.SetNumberOfComponents(3)
    for face in shape.faces():
        tri=BRep_Tool.Triangulation_s(face.wrapped,TopLoc_Location())
        surf=BRepAdaptor_Surface(face.wrapped)
        sign=-1 if face.wrapped.Orientation()==TopAbs_REVERSED else 1
        for i in range(1,tri.NbNodes()+1):
            uv=tri.UVNode(i);props=BRepLProp_SLProps(surf,uv.X(),uv.Y(),1,1e-7);n=props.Normal()
            normals.InsertNextTuple3(-sign*n.X(),sign*n.Z(),sign*n.Y())
    points=vtk.vtkPoints()
    for v in vertices:points.InsertNextPoint(-v.X,v.Z,v.Y)
    cells=vtk.vtkCellArray()
    for tri in triangles:
        cells.InsertNextCell(3)
        for i in tri:cells.InsertCellPoint(i)
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    assert normals.GetNumberOfTuples()==len(vertices)
    poly.GetPointData().SetNormals(normals)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
    # Paint masks use true model millimetres, not VTK's normalized VBO frame.
    mapper.SetVBOShiftScaleMethod(vtk.vtkOpenGLPolyDataMapper.DISABLE_SHIFT_SCALE)
    actor=vtk.vtkActor();actor.SetMapper(mapper)
    prop=actor.GetProperty();prop.SetColor(*col);prop.SetAmbient(1 if emission else .25)
    prop.SetDiffuse(0 if emission else .78);prop.SetSpecular(.10);prop.SetSpecularPower(28);prop.SetInterpolationToPhong()
    if painted and label=='Piku_cat_body':paint_shader(actor,proposed)
    renderer.AddActor(actor)
    return actor,emission

def label(renderer,title,subtitle):
    for text,y,size,color in [(title,1260,30,(.17,.19,.21)),(subtitle,1220,21,(.36,.39,.42))]:
        actor=vtk.vtkTextActor();actor.SetInput(text);actor.SetPosition(35,y)
        p=actor.GetTextProperty();p.SetFontSize(size);p.SetColor(*color)
        renderer.AddViewProp(actor)

def scene(parts,proposed,painted,with_labels=True):
    renderer=vtk.vtkRenderer();renderer.SetBackground(.966,.956,.936)
    pixels=[]
    for shape in parts:
        a,emission=add_shape(renderer,shape,painted,proposed)
        if emission:pixels.append(a)
    for pos,power in [((-130,-170,240),.9),((110,140,170),.5)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(0,18,45);light.SetIntensity(power);renderer.AddLight(light)
    cam=renderer.GetActiveCamera();cam.SetFocalPoint(-2,18,48);cam.SetViewUp(0,0,1)
    cam.ParallelProjectionOn();cam.SetParallelScale(63);cam.SetClippingRange(80,500)
    if with_labels:
        label(renderer,'REFINED' if proposed else 'EARLIER PROPORTIONS',
              'Head volume -8.0%  |  Torso form +6.4%' if proposed else 'Piku-cat before the proportion refinement')
    return renderer,pixels

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--painted-only',action='store_true');parser.add_argument('--single',action='store_true');args=parser.parse_args()
    if args.single:
        renderer,pixels=scene(proposed_parts(),True,True,False)
        cam=renderer.GetActiveCamera();cam.SetPosition(-115,-255,118);cam.SetParallelScale(59)
        window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1750);window.SetMultiSamples(8);window.AddRenderer(renderer)
        window.Render()
        capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update()
        path=root/'Piku-cat-preview.png'
        writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
        window.Finalize();print(json.dumps({'actual_CAD':True,'painted':True,'OLED_on':True,'image':str(path)}),flush=True)
        return
    folder=root/'previews';folder.mkdir(exist_ok=True)
    parts=[current_parts(),proposed_parts()]
    saved=[]
    for painted in ([True] if args.painted_only else [False,True]):
        window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(2400,1350);window.SetMultiSamples(8)
        scenes=[scene(p,i==1,painted) for i,p in enumerate(parts)]
        for i,(renderer,pixels) in enumerate(scenes):
            renderer.SetViewport(i*.5,0,(i+1)*.5,1);window.AddRenderer(renderer)
            for a in pixels:a.SetVisibility(painted)
        views=[('front',(0,-280,48)),('three-quarter',(-115,-255,118)),('side',(-285,18,65))] if not painted else [('painted',(-115,-255,118))]
        for name,pos in views:
            for renderer,_ in scenes:renderer.GetActiveCamera().SetPosition(*pos)
            window.Render()
            capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update()
            path=folder/f'comparison-{name}.png'
            writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
            saved.append(str(path));print(str(path),flush=True)
        window.Finalize()
    print(json.dumps({'actual_CAD':True,'matched_camera_scale_lighting':True,'images':saved}),flush=True)

if __name__=='__main__':main()
