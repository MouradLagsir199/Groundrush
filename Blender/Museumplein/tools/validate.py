import bpy,numpy as np,bmesh,json,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene;n=s['Iteration'];qpath=R+'/validation.json';qa=json.load(open(qpath));vs=fs=0;bad=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 a=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',a);vs+=len(a)//3;fs+=len(ob.data.polygons)
 if not np.isfinite(a).all():bad.append(ob.name)
assert not bad
ride=bpy.data.objects['Continuous high density riding surface'];a=np.empty(len(ride.data.vertices)*3,np.float32);ride.data.vertices.foreach_get('co',a);a=a.reshape(-1,3);N=len(a)//2;assert np.max(abs(a[:N,2]-a[N:,2]-.16))<1e-5
bpy.context.view_layer.update();bv=BVHTree.FromObject(ride,bpy.context.evaluated_depsgraph_get());contacts=[];closed=[]
for ob in s.objects:
 if ob.type!='MESH' or not ob.name.startswith(('Coping north','Coping court raised','East low rail','Middle bank rail','Lower bank rail','Funbox bank rail','Funbox lower rail','Stair handrail','Double arch')):continue
 bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert bad==0,ob.name;closed.append(ob.name)
 if 'continuous topbar' in ob.name or 'flat-bar arch' in ob.name or ob.name.startswith(('Double arch outer','Double arch nested')):
  a=np.array([tuple(v.co) for v in ob.data.vertices])
  for ring in [a[:36],a[-36:]]:
   p=ring.mean(axis=0);hit=bv.ray_cast(Vector((p[0],p[1],8)),Vector((0,0,-1)))[0];gap=p[2]-hit.z;assert gap<.0002;contacts.append(float(gap))
north=bpy.data.objects['North quarter photo traced round returns'];bn=BVHTree.FromObject(north,bpy.context.evaluated_depsgraph_get());dist=[]
for label in ['north_trace_uv','south_trace_uv']:
 for u,v in qa[label]:
  p=Vector(((u-960)*.025,(640-v)*.025,1.34));hit=bn.find_nearest(p)[0];dist.append((hit-p).length)
assert max(dist)<.01
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
qa['fresh_validation']={'reopened':os.path.relpath(bpy.data.filepath,os.path.dirname(os.path.dirname(R))),'vertices':vs,'faces':fs,'non_finite_meshes':[],'closed_coping_and_rail_meshes':len(closed),'grounded_rail_endpoints':len(contacts),'north_contact_samples':len(dist),'north_max_surface_distance_m':max(dist),'packed_textures':True,'slab_thickness_m':.16};open(qpath,'w').write(json.dumps(qa,indent=2));print('ROUND VALIDATION PASSED',n,qa['fresh_validation'],flush=True)
