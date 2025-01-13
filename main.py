from repo import Repo

sampleRepo = Repo()

sampleRepo.create(5, 10,10, 64, 'green')
sampleRepo.list() # F571 will be listed with an id

ogr = sampleRepo.attach(5, "onur")
tgr = sampleRepo.attach(5, "tolga") # these two are the same object

print(sampleRepo.listattached("onur"))
sampleRepo.components.list()

rt = sampleRepo.components.create('turn90')
sampleRepo.objects[5][(3,3)] = rt

ogr[(1,1)] = rt
rt.rotation = 0

for j in range(2,8):
    ogr[(1,j)] = sampleRepo.components.create('straight')
    ogr[(1,j)].rotation = 0



dt = sampleRepo.components.create('turn90')
dt.rotation = 1
ogr[(1,8)] = dt

for i in range(2,8):
    ogr[(i,1)] = sampleRepo.components.create('straight')
    ogr[(i,8)] = sampleRepo.components.create('straight')
    ogr[(i,1)].rotation = 1
    ogr[(i,8)].rotation = 1

rt = sampleRepo.components.create('turn90')
ogr[(8,1)] = rt
rt.rotation = 3

for j in range(2,8):
    ogr[(8,j)] = sampleRepo.components.create('straight')
    ogr[(8,j)].rotation = 0

dt = sampleRepo.components.create('turn90')
dt.rotation = 2
ogr[(8,8)] = dt
ogr[(1,3)] = sampleRepo.components.create('booster')
ogr[(0,0)] = sampleRepo.components.create('straight')
ogr[(1,0)] = sampleRepo.components.create('straight')
ogr[(0,2)] = sampleRepo.components.create('straight')
ogr[(0,1)] = sampleRepo.components.create('straight')
ogr[(0,0)] = sampleRepo.components.create('straight')
ogr[(0,8)] = sampleRepo.components.create('straight')
ogr[(1,0)] = sampleRepo.components.create('rock')
ogr[(7,1)] = sampleRepo.components.create('fuel')


a = ogr.components.create('Merso')
frr = ogr.components.create('Ferrari')


a.speed = 60
frr.pos = (65,65)
frr.start()
a.start()
a.tick()
a.tick()
a.tick()
frr.tick()
ogr[(0,1)] = sampleRepo.components.create('checkpoint')
print(ogr.draw())


frr.driver = "Alonso"


frr.accel()
frr.accel()

frr.tick()
frr.accel()

frr.tick()
frr.accel()

frr.tick()
frr.accel()

frr.tick()
frr.accel()

frr.tick()
frr.accel()

frr.tick()

frr.tick()

frr.accel()
frr.tick()
frr.accel()
frr.tick()
frr.accel()
frr.tick()
frr.accel()





