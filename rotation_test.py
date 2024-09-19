#!/usr/bin/python

import carla 
import math 
import random 
import time 


# Connect the client and set up bp library and spawn points
client = carla.Client('localhost', 2000) 
world = client.get_world()
bp_lib = world.get_blueprint_library()  
spawn_points = world.get_map().get_spawn_points() 

#clean up all other actors
for v in world.get_actors().filter('*vehicle*'): 
    v.destroy()

# Add the ego vehicle
vehicle_bp = bp_lib.find('vehicle.mini.cooper_s_2021') 
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[0])


forward_vector = carla.Vector3D(x=1.0, y=1.0, z=0.0)

desired_yaw = math.degrees(math.atan2(forward_vector.y, forward_vector.x))
steer = (desired_yaw - vehicle.get_transform().rotation.yaw / 180)
throttle = 1.0
vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=0.0))

