#!/usr/bin/python

import carla
import math
import random
import time

client = carla.Client('localhost', 2000) #client

world = client.get_world() #gets world
bp_lib = world.get_blueprint_library() #gets all vehicles
spawn_points = world.get_map().get_spawn_points() #get all spawn points
spectator = world.get_spectator() #get spectator

town_map = world.get_map() #gets map
roads = town_map.get_topology()

vehicle_bp = bp_lib.find('vehicle.tesla.model3') #get blue car
start_point = spawn_points[0] #select first spawn point

vehicle = world.try_spawn_actor(vehicle_bp, start_point) #spawn Car at start point
print("Starting Position:", start_point) #print start point coords

#Check if the vehicle was spawned
if vehicle is not None:
    print("Vehicle spawned at:", start_point.location)
    
    #Enable autopilot
    vehicle.set_autopilot(True)

    vehiclepos_spectator= carla.Transform(vehicle.get_transform().transform(carla.Location(x=-10,z=3)),vehicle.get_transform().rotation)
    #spectator.set_transform(vehiclepos_spectator)

    #Keep the autopilot running
    while True:
        #Update spectator to follow the vehicle
        #vehiclepos_spectator= carla.Transform(vehicle.get_transform().transform(carla.Location(x=-10,z=3)),vehicle.get_transform().rotation)
        #spectator.set_transform(vehiclepos_spectator)
        
        time.sleep(0.05)
else:
    print("Vehicle could not be spawned. Please check spawn point and try again.")

#for i in range(30):
   # vehicle_bp = random.choice(bp_lib.filter('vehicle'))
    #npc = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points))
    
#for v in world.get_actors().filter('vehicle'):
   # v.set_autopilot(True)
