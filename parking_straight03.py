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

#set the vehicle to the desired location #x=7.561335, y=111.042351, z=0.931391
vehicle.set_transform(carla.Transform(carla.Location(x=7.561335, y=111.042351, z=0.931391), carla.Rotation(pitch=0.016720, yaw=0.187248, roll=0.000006)))

# Move the spectator
spectator = world.get_spectator() 
spec_transform = carla.Transform(carla.Location(x=15.012684, y=150.451126, z=52.484871), carla.Rotation(pitch=-32.483482, yaw=-89.044197, roll=0.000016))
spectator.set_transform(spec_transform)


#print(roads)
#first_waypoint = roads[0][0]

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

 #logic to drive the car in a straight line to the predefined parking lot
def park_logic_straight(target_transform):
    while True:
        current_velocity = vehicle.get_velocity()
        current_speed = current_velocity.length()

        current_transform = vehicle.get_transform()

        direction = target_transform.location - current_transform.location
        distance = direction.length()

        desired_yaw = math.degrees(math.atan2(direction.y, direction.x))

        steer = (desired_yaw - current_transform.rotation.yaw) / 180

       # print(distance)

        if current_speed > max_speed: 
            throttle = 0.0
            brake = 0.1
        elif distance > 0.1:
            throttle = 0.5
            brake = 0.0
        else:
            throttle = 0.0
            brake = 1.0
        
        vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

        if distance < 0.3:
            throttle = 0.0
            brake = 1.0
            vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))
            break

def turn_right():
    time = 0    
    while True:
        time = time + 1
       # print(time)
      #  print(vehicle.get_transform().rotation.yaw)
        if vehicle.get_transform().rotation.yaw > -90:
            break
        throttle = 0.2
        steer = 1.0
        brake = 0.0
        vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))
    throttle = 0.0
    steer = 0.0
    brake = 1.0
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

    

def turn_left():
    time = 0    
    while True:
        time = time + 1
        #print(time)
        if time > 2900000:
            break
        throttle = 0.2
        steer = -1.0
        brake = 0.0
        vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))
    throttle = 0.0
    steer = 0.0
    brake = 1.0
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

#Location(x=7.561333, y=111.042351, z=0.683554)

#the Route to the parking_lot 3
def drive_to_parking_lot03():
    show_route(vehicle.get_location(),point_b)
    agent = BasicAgent(vehicle)
    agent.set_destination(point_b)
    agent.set_target_speed(20) #set The maximum speed of the car

    while True:
        if agent.done():
            print('Target Location reached!')
            break
        vehicle.apply_control(agent.run_step())

    #The parking lot:
    parking_space = carla.Transform(carla.Location(x=81.395195, y=32.000763, z=-0.004640), carla.Rotation(pitch=-0.009979, yaw=-86.966881, roll=0.000049))


    time.sleep(1)
    turn_right()
    time.sleep(0.5)
    park_logic_straight(parking_space)

#The way to the parking lot is
def drive_to_parking_lot01():   
    show_route(vehicle.get_location(),point_c)

    agent = BasicAgent(vehicle)
    agent.set_destination(point_c)
    agent.set_target_speed(20) #set The maximum speed of the car

    while True:
        if agent.done():
            print('Target Location reached!')
            break
        vehicle.apply_control(agent.run_step())

    parking_space1 = carla.Transform(carla.Location(x=76.347740, y=31.460554, z=-0.004596), carla.Rotation(pitch=-0.002992, yaw=-88.150383, roll=0.000544))

    time.sleep(1)
    turn_right()
    time.sleep(0.5)
    park_logic_straight(parking_space1)

drive_to_parking_lot03()