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
vehicle2 = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))


spectator = world.get_spectator()

vehiclepos_spectator= carla.Transform(vehicle.get_transform().transform(carla.Location(x=-40,z=3)),vehicle.get_transform().rotation)
spectatorpos = carla.Transform(spectator.get_transform().transform(carla.Location(x=0,z=0)),spectator.get_transform().rotation)

spectator.set_transform(vehiclepos_spectator)
time.sleep(1.0)
#Get vehicle Pos on the ground
vehiclepos= carla.Transform(vehicle.get_transform().transform(carla.Location(x=0,z=0)),vehicle.get_transform().rotation)


for i in range(30):
    vehicle_bp = random.choice(bp_lib.filter('vehicle'))
    npc = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))
    npc.set_transform(vehiclepos)
vehicle2.set_transform(vehiclepos)
