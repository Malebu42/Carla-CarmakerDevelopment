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

start_point = spawn_points[0] #select first spawn point
spectator_pos = carla.Transform(start_point.location + carla.Location(x=20,y=10,z=4),
                                carla.Rotation(yaw = start_point.rotation.yaw -155))

#set spectator
spectator.set_transform(spectator_pos)

#camera mount offset on the car - you can tweak these to have the car in view or not
CAMERA_POS_Z = 3 
CAMERA_POS_X = -5 

# Spawn multiple NPC vehicles
vehicles_list = []

for i in range(30):
#for i, spawn_point in enumerate(spawn_points):
    vehicle_bp = random.choice(bp_lib.filter('vehicle'))  # Random vehicle blueprint
    spawn_point = random.choice(spawn_points)  # Random spawn point
    npc = world.try_spawn_actor(vehicle_bp, spawn_point)
    
    if npc is not None:  # Ensure NPC was spawned successfully
        vehicles_list.append(npc)  # Store reference to clean up later

for vehicle in vehicles_list:
    vehicle.set_autopilot(True)  # Enable autopilot for the NPC vehicle

# Main loop to keep autopilot active
try:
    while True:
        time.sleep(0.05)  # Wait for a short time
except KeyboardInterrupt:
    print("Simulation stopped manually.")
finally:
    # Clean up vehicles when exiting
    for vehicle in vehicles_list:
        vehicle.destroy()

