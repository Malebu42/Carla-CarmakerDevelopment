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

vehicle_bp = bp_lib.find('vehicle.carlamotors.firetruck') #vehicle.tesla.model3 to get blue car
start_point = spawn_points[0] #select first spawn point

vehicle = world.try_spawn_actor(vehicle_bp, start_point) #spawn Car at start point
print("Starting Position:", start_point) #print start point coords

#Check if the vehicle was spawned
if vehicle is not None:
    print("Vehicle spawned at:", start_point.location)
    
else:
    print("Vehicle could not be spawned. Please check spawn point and try again.")

# now we define 2 cars
truck_bp = world.get_blueprint_library().filter('*firetruck*')
mini_bp = world.get_blueprint_library().filter('*cooper_s*')

#start first car in alredy defined start point
truck = world.try_spawn_actor(truck_bp[0], start_point)
# tweak spectator position to watch the show

spectator = world.get_spectator()
spawn_points = world.get_map().get_spawn_points()
start_point = spawn_points[0]

spectator_pos = carla.Transform(start_point.location + carla.Location(x=20,y=10,z=4),
                                carla.Rotation(yaw = start_point.rotation.yaw -155))

spectator.set_transform(spectator_pos)

# drop the Mini from the sky 

#spawn it first somewhere else
mini = world.try_spawn_actor(mini_bp[0], spawn_points[10])

mini_pos = carla.Transform(start_point.location + carla.Location(x=-4,z=10),
                            carla.Rotation(yaw = start_point.rotation.yaw - 0))
mini.set_transform(mini_pos)