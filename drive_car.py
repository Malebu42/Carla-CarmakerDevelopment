#!/usr/bin/python

import carla 
import math 
import random 
import time 


# Connect the client and set up bp library and spawn points
client = carla.Client('localhost', 2000) 
world = client.get_world()
spectator = world.get_spectator() 
bp_lib = world.get_blueprint_library()  
spawn_points = world.get_map().get_spawn_points() 

#clean up all other actors
for v in world.get_actors().filter('*vehicle*'): 
    v.destroy()

# Add the ego vehicle
vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020') 
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[13])

#set the vehicle to the desired location
vehicle.set_transform(carla.Transform(carla.Location(x=7.561335, y=111.042351, z=0.931391), carla.Rotation(pitch=8.095427, yaw=-4.816957, roll=0.000086)))

# Move the spectator
spec_transform = carla.Transform(carla.Location(x=15.012684, y=150.451126, z=52.484871), carla.Rotation(pitch=-32.483482, yaw=-89.044197, roll=0.000016))
spectator.set_transform(spec_transform)

#get the map and map waypoints
town_map = world.get_map()
roads = town_map.get_topology()
vehicle_location = vehicle.get_location()

#print(roads)
#first_waypoint = roads[0][0]

import sys
sys.path.append('/home/ubuntu/CARLA_0.9.14/PythonAPI/carla') 
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.basic_agent import BasicAgent

#Trace Route as blue dotted line
sampling_resolution = 2
grp = GlobalRoutePlanner(town_map, sampling_resolution)

point_a = vehicle_location
point_b = carla.Location(x=81.05, y=33.19, z=1.85)
route = grp.trace_route(point_a,point_b)

for waypoint in route :
    world.debug.draw_string(waypoint[0].transform.location, '^', draw_shadow=False, 
        color=carla.Color(r=0, g=0,b=255), life_time=120,
        persistent_lines=True)

#Move the Vehicle to the destination:
agent = BasicAgent(vehicle)
agent.set_destination(point_b)
agent.set_target_speed(30) #set The maimum speed of the car

while True:
    if agent.done():
        print('Target Location reached!')
        break
    vehicle.apply_control(agent.run_step())




