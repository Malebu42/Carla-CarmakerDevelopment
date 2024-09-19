#!/usr/bin/python

import carla
import math
import random
import time

client = carla.Client('localhost', 2000) 
world = client.get_world()

bp_lib = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020')
vehicle = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))

for i in range(10):
    vehicle_bp = random.choice(bp_lib.filter('vehicle'))
    npc = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))

spectator = world.get_spectator()

vehiclepos_spectator= carla.Transform(vehicle.get_transform().transform(carla.Location(x=-40,z=3)),vehicle.get_transform().rotation)
spectator.set_transform(vehiclepos_spectator)


tm = client.get_trafficmanager(8000)
tm.set_synchronous_mode(True)

camera_bp = bp_lib.find('sensor.camera.rgb')

camera_init_trans = carla.Transform(carla.Location(z=2))

camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=vehicle)

camera.listen(lambda image: image.save_to_disk('/examples/_out'.format(image.frame)))
#camera.listen(lambda image: image.save_to_disk('examples/_out' % image.frame))

camera.stop()

while True:
    world.tick()
    for v in world.get_actors().filter('*vehicle*'):
        v.set_autopilot(True)

