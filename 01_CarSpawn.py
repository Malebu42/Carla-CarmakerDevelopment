#!/usr/bin/python

import carla
import math
import random
import time
import cv2 #to work with images from cameras
import numpy as np #in this example to change image representation - re-shaping

client = carla.Client('localhost', 2000) #client

world = client.get_world() #gets world
bp_lib = world.get_blueprint_library() #gets all vehicles
spawn_points = world.get_map().get_spawn_points() #get all spawn points
spectator = world.get_spectator() #get spectator

vehicle_bp = bp_lib.find('vehicle.tesla.model3') #vehicle.tesla.model3 to get blue car
start_point = spawn_points[0] #select first spawn point

vehicle = world.try_spawn_actor(vehicle_bp, start_point) #spawn Car at start point
print("Starting Position:", start_point) #print start point coords

spectator_pos = carla.Transform(start_point.location + carla.Location(x=20,y=10,z=4),
                                carla.Rotation(yaw = start_point.rotation.yaw -155))

spectator.set_transform(spectator_pos)

#Check if the vehicle was spawned
if vehicle is not None:
    print("Vehicle spawned at:", start_point.location)
    
else:
    print("Vehicle could not be spawned. Please check spawn point and try again.")

