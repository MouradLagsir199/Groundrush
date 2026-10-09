import bpy,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene
for name,key in [('28 north round shoulders','north'),('28 north plan','north_plan'),('28 court coping','court'),('28 court plan','court_plan'),('29 full photo01 plan','full_plan')]:
 s.camera=bpy.data.objects[name];s.render.resolution_x=1919 if key=='full_plan' else 1200;s.render.resolution_y=1279 if key=='full_plan' else 900;s.cycles.samples=32;s.render.filepath=R+'/review/'+key+'.png';bpy.ops.render.render(write_still=True)
