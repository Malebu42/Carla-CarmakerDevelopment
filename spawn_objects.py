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

for i in range(100):
    world.try_spawn_actor(random.choice(bp_lib), random.choice(spawn_points))

