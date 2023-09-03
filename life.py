import numpy as np
import random
import open3d as o3d
import time

# create a simple NxNxN cube for our data
xdim = 15
ydim = 15
zdim = 15
vol = np.zeros((zdim,ydim,xdim,3))
col = np.zeros((zdim,ydim,xdim,3))

# assign each point in the point cloud to a position, and trivially I'm making a cube of these where the indices are the locations
for z in range(zdim):
    for y in range(ydim):
        for x in range(xdim):
            vol[z,y,x] = (x,y,z)
            # col[z,y,x] = (1,1,1)

# seed the cube with 20 random start colors
# note that open3d wants colors in the 0.0 to 1.0 range for RGB
random.seed(1134)
for i in range(20):
    x = random.randrange(xdim-2) + 1
    y = random.randrange(ydim-2) + 1
    z = random.randrange(zdim-2) + 1

    r = random.random()
    b = random.random()
    g = random.random()

    col[z,y,x] = (r,g,b)

# create a point cloud object to render our data
# this is a very simple point cloud example, but you could use spheres, etc to render instead
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(vol.reshape(xdim*ydim*zdim,3))
pcd.colors = o3d.utility.Vector3dVector(col.reshape(xdim*ydim*zdim,3))

# simple sim that distributes the colors over time based on neighbors and thresholds
def updateSim():
    neighbors = np.zeros(3)
    col2 = np.copy(col)
    aliveThresh = 1.0
    xfrRate = 0.1
    for z in range(1,zdim-1):
        for y in range(1,ydim-1):
            for x in range(1,xdim-1):
                neighborColors = (0,0,0) # cumulative color of included neighbors
                aliveNeighbors = 0
                for dz in range(-1,2):
                    for dy in range(-1,2):
                        for dx in range(-1,2):
                            c = col[z+dz,y+dy,x+dx]
                            if c[0] + c[1] + c[2] > aliveThresh:
                                aliveNeighbors += 1
                                neighborColors += c
                alive = False
                c = col[z,y,x]
                if c[0] + c[1] + c[2] > aliveThresh:
                    aliveNeighbors -= 1 # don't count self
                    alive = True
                if alive and aliveNeighbors > 3:
                    col2[z,y,x] *= (1.0-xfrRate)
                elif not alive and aliveNeighbors > 1:
                    col2[z,y,x] += xfrRate * neighborColors/aliveNeighbors

    col2.clip(0.0,1.0,out=col) # clip & copy back to current 3D array
    # tell the point cloud object that our data has changed (probably a better way to do this, this feels like a large copy to me)
    pcd.colors = o3d.utility.Vector3dVector(col.reshape(xdim*ydim*zdim,3))

quitRequest = False
def key_action_callback(vis, key, action):
    print('key', key, action) # key 1/0 is press/release, actions are 0=none, 1=shift, 2=ctrl, 3=ctrl+shift, 4=alt, 5=alt+shift, 6=ctrl+alt
    global quitRequest
    quitRequest = True

# create a simple visualizer to render our point cloud
#vis = o3d.visualization.Visualizer()
vis = o3d.visualization.VisualizerWithKeyCallback()
vis.create_window()
vis.add_geometry(pcd) # adds the point cloud object
vis.register_key_action_callback(81, key_action_callback) # 81 is asci for lowercase q
opt = vis.get_render_option()
opt.background_color = np.asarray([0, 0, 0])

# sets the point size in the window
# point cloud look a little weird, the size never changes as you zoom in/out
# also the black points will render also, and can oclude the bright points.
# Open3D seems to sort, so adding transparency would make sense, but I never found an easy way to do this with point clouds
# other geometry types allow for lit surfaces with materials that include transparency
vis.get_render_option().point_size = 10.0

# just loop for a while updating our simulation
frame = 0
while frame < 10000 and not quitRequest:
    #updateSim() # if this were fast, I could update every frame and also throttle the propegation speed of the clors
    vis.update_geometry(pcd)
    vis.update_renderer()
    vis.poll_events()
    frame += 1
    if frame % 10 == 0:
        #print('frame: %d' % frame)
        updateSim() # sim update is crazy slow, so I'm just doing once per 100 frames
    time.sleep(0.01) # slowing us down to a reasonable frame rate
vis.destroy_window()

