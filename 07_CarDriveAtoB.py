#!/usr/bin/python

import carla 
import math 
import random 
import time 
import pygame

import sys
sys.path.append('/home/ubuntu/CARLA_0.9.14/PythonAPI/carla') 
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.basic_agent import BasicAgent
from agents.navigation.behavior_agent import BehaviorAgent

#set up window
pygame.init()
screen = pygame.display.set_mode((640, 480))

# Connect the client and set up bp library and spawn points
client = carla.Client('localhost', 2000) 
world = client.get_world()
#load blue prints and get world spawn points
bp_lib = world.get_blueprint_library()  
spawn_points = world.get_map().get_spawn_points() 

#clean up all other actors
for v in world.get_actors().filter('*vehicle*'): 
    v.destroy()

# Add the Hero vehicle
vehicle_bp = bp_lib.find('vehicle.tesla.model3') 
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[13])

#set the vehicle to the desired location 
vehicle.set_transform(carla.Transform(carla.Location(x=50, y=51.404888, z=0.000331), carla.Rotation(pitch=0.003832, yaw=179.913284, roll=0.000000)))
posA = vehicle.set_transform(carla.Transform(carla.Location(x=50, y=51.404888, z=0.000331), carla.Rotation(pitch=0.003832, yaw=179.913284, roll=0.000000)))

# Move the spectator
spectator = world.get_spectator() 
#spec_transform1 = carla.Transform(carla.Location(x=50, y=73.267792, z=19.089298), carla.Rotation(pitch=-33.959076, yaw=-88.764702, roll=0.000016))
#spectator.set_transform(spec_transform1)

camera_mode = "first_person" #define 

def update_camera():
    global camera_mode
    # Get the vehicle's transform
    transform = vehicle.get_transform()

    if camera_mode == "first_person":
        # First-person view: Inside the car (driver's seat)
        camera_location = carla.Location(x=-0, y=-0.4, z=1.2)  # Adjust inside the car
        camera_rotation = transform.rotation  # Sync with vehicle rotation

    elif camera_mode == "third_person":
        # Third-person view: Behind and above the car
        camera_location = carla.Location(x=-10.0, y=0.0, z=3)  # Adjust behind the car
        camera_rotation = transform.rotation  # Sync with vehicle rotation
    
   # Apply the camera position relative to the vehicle's current transform
    spectator_transform = carla.Transform(transform.transform(camera_location), camera_rotation)
    # Update the spectator camera transform
    spectator.set_transform(spectator_transform)

# Function to toggle between first-person and third-person views
def toggle_camera_mode():
    global camera_mode
    if camera_mode == "first_person":
        camera_mode = "third_person"
        print("Switched to third-person view")
    else:
        camera_mode = "first_person"
        print("Switched to first-person view")

# Wait for the vehicle to spawn
time.sleep(1)

# Set up the BasicAgent to control the vehicle
agent = BasicAgent(vehicle)
#agent = BehaviorAgent(vehicle, behavior='normal')

# Set a target speed for the agent (in km/h)
agent.set_target_speed(40) 
agent.follow_speed_limits = True

# Select a random spawn point as the destination
random_spawn_point = random.choice(spawn_points)
posB = random_spawn_point 

# Set the destination for the agent to drive to
destination = random_spawn_point.location
agent.set_destination(destination)

print(f"Vehicle is driving to: {destination}")

# Drive the vehicle to the destination
while True:
    update_camera()
    # Check for 'C' key press to toggle camera mode using pygame
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Press 'C' to toggle views
                toggle_camera_mode()


    if vehicle.get_location().distance(destination) < 2.0:  # Stop when near the destination
        print("arrvied at B!")
        break
    elif vehicle.get_location().distance(destination) < 50:
        agent.set_target_speed(30) 
    
    control_command = agent.run_step()  # Get control commands from the agent
    vehicle.apply_control(control_command)  # Apply control to the vehicle
    
    #time.sleep(0.05)

# Move the spectator to view the vehicle at the destination
spectator = world.get_spectator()
spectator_transform = carla.Transform(
    carla.Location(x=destination.x, y=destination.y + 20, z=19),
    carla.Rotation(pitch=-30, yaw=0, roll=0)
)
spectator.set_transform(spectator_transform)

