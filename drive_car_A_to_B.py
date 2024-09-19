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
vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020') 
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[13])

#add the two obstacle vehicles
vehicle_bp1 = bp_lib.find('vehicle.lincoln.mkz_2020') 
vehicle1 = world.try_spawn_actor(vehicle_bp, spawn_points[0])
vehicle_bp2 = bp_lib.find('vehicle.lincoln.mkz_2020') 
vehicle2 = world.try_spawn_actor(vehicle_bp, spawn_points[1])

#set the vehicle to the desired location #x=7.561335, y=111.042351, z=0.931391
vehicle.set_transform(carla.Transform(carla.Location(x=-16.633558, y=51.404888, z=0.000331), carla.Rotation(pitch=0.003832, yaw=179.913284, roll=0.000000)))


#set the obstacle vehicle locations
vehicle1.set_transform(carla.Transform(carla.Location(x=-40.242737, y=48.828754, z=0.000326), carla.Rotation(pitch=-0.001373, yaw=178.527618, roll=0.000000)))
vehicle2.set_transform(carla.Transform(carla.Location(x=-27.447462, y=48.828754, z=-0.000326), carla.Rotation(pitch=-0.001373, yaw=178.527618, roll=0.000000)))


# Move the spectator
spectator = world.get_spectator() 
#spec_transform = carla.Transform(carla.Location(x=15.012684, y=150.451126, z=52.484871), carla.Rotation(pitch=-32.483482, yaw=-89.044197, roll=0.000016))
spec_transform1 = carla.Transform(carla.Location(x=-26.003437, y=73.267792, z=19.089298), carla.Rotation(pitch=-33.959076, yaw=-88.764702, roll=0.000016))

spectator.set_transform(spec_transform1)


#print(roads)
#first_waypoint = roads[0][0]

#first_obstacle_car: Transform(Location(x=-40.242737, y=48.828754, z=0.000326), Rotation(pitch=-0.001373, yaw=178.527618, roll=0.000000))


import sys
sys.path.append('/home/ubuntu/CARLA_0.9.14/PythonAPI/carla') 
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.basic_agent import BasicAgent

point_b = carla.Location(x=79.968552, y=52.354538, z=-0.001338) #Position right in front of the parking
point_c = carla.Location(x=73.951416, y=52.221897, z=-0.004662)

#Trace Route as blue dotted line
def show_route(a,b):
    town_map = world.get_map()
    sampling_resolution = 2

    grp = GlobalRoutePlanner(town_map, sampling_resolution)
    route = grp.trace_route(a,b)

    for waypoint in route :
        world.debug.draw_string(waypoint[0].transform.location, '^', draw_shadow=False, 
            color=carla.Color(r=0, g=0,b=255), life_time=120,
            persistent_lines=True)
        

max_speed = 5 / 3.6

#reverse = True

while True:

    start = vehicle.get_location()
    end = carla.Location(x=-40.032120, y=50.804287, z=0.000336)

    dx = start.x - end.x
    dy = start.y - end.y
    dz = start.z - end.z

    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    print(distance)

    
    if distance < 1:
        break
    if distance > 10:
        throttle = 0.5
        steer = 0.0
        brake = 0.0
        vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))
    elif distance > 5:
        throttle = 0.3
        steer = 0.0
        brake = 0.0
        vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))
  
throttle = 0.0
steer = 0.0
brake = 1.0
vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

seconds = 0

while True:
    print(seconds)
    seconds = seconds + 1
    if seconds > 1000000:
        break
    throttle = 0.5
    steer = 0.5
    brake = 0.0
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))
throttle = 0.0
steer = 0.0
brake = 1.0
vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))

time.sleep(0.5)

seconds = 0
while True:
    print(seconds)
    seconds = seconds + 1
    if seconds > 570000: #straigth line into the parking lot
        break
    throttle = 0.5
    steer = 0.0
    brake = 0.0
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))
throttle = 0.0
steer = 0.0
brake = 1.0
vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))

time.sleep(0.5)

seconds = 0
while True:
    print(seconds)
    seconds = seconds + 1
    if seconds > 580000:
        break
    throttle = 0.5
    steer = -1
    brake = 0.0
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))
throttle = 0.0
steer = 0.0
brake = 1.0
vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake, reverse = True))



