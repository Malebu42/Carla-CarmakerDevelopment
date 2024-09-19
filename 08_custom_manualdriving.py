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
screen = pygame.display.set_mode((1200, 600))

# Connect to the CARLA server
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# Load the blueprint library and get the spawn points
bp_lib = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

# Clean up all existing vehicles
for v in world.get_actors().filter('*vehicle*'):
    v.destroy()

# Spawn a Tesla Model 3 vehicle at a predetermined spawn point
vehicle_bp = bp_lib.find('vehicle.tesla.model3')
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[0])

# Wait for the vehicle to spawn
time.sleep(1)

# Set up the spectator camera to simulate first-person and third-person perspectives
spectator = world.get_spectator()

# Define camera modes
camera_mode = "first_person"  # Default camera mode (can toggle with keyboard)

# Initialize vehicle control variables
throttle = 0.0
steer = 0.0
brake = 0.0
reverse = False

# Function to update the camera position
def update_camera():
    global camera_mode
    transform = vehicle.get_transform()

    if camera_mode == "first_person":
        # First-person view: Inside the car (driver's seat)
        camera_location = carla.Location(x=-0.1, y=-0.4, z=1.2)  # Adjust inside the car
        camera_rotation = transform.rotation  # Sync with vehicle rotation

    elif camera_mode == "third_person":
        # Third-person view: Behind and above the car
        camera_location = carla.Location(x=-6.0, y=0.0, z=2.5)  # Adjust behind the car
        camera_rotation = transform.rotation  # Sync with vehicle rotation

    # Apply the camera position relative to the vehicle's current transform
    spectator_transform = carla.Transform(transform.transform(camera_location), camera_rotation)
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

# Function to handle manual vehicle controls
def handle_vehicle_controls():
    global throttle, steer, brake, reverse

    # Reset controls
    throttle = 0.0
    brake = 0.0
    steer = 0.0

    keys = pygame.key.get_pressed()

    # Throttle (W key)
    if keys[pygame.K_w]:
        throttle = 1.0  # Max throttle

    # Brake/Reverse (S key)
    if keys[pygame.K_s]:
        if vehicle.get_velocity().length() > 0.1:  # Apply brake when moving
            brake = 1.0
        else:
            throttle = -0.5  # Reverse when stopped

    # Steer left (A key)
    if keys[pygame.K_a]:
        steer = -1.0  # Max steer left

    # Steer right (D key)
    if keys[pygame.K_d]:
        steer = 1.0  # Max steer right

    # Apply vehicle controls
    vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake=brake))

# Main loop to simulate driving and update camera position
try:
    while True:
        # Handle vehicle controls
        handle_vehicle_controls()

        # Update the camera based on the current mode
        update_camera()

        # Check for events (e.g., key presses)
        for event in pygame.event.get():
            # Quit the simulation if the window is closed
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Toggle camera mode when 'C' is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                toggle_camera_mode()

        time.sleep(0.001)  # Maintain simulation speed

except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    pygame.quit()  # Quit pygame when the simulation ends