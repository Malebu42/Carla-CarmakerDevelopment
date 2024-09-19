#!/usr/bin/python

import carla
import math
import random
import time
import pygame

# Only for map Town-05

import sys
sys.path.append('/home/ubuntu/CARLA_0.9.14/PythonAPI/carla')
from agents.navigation.global_route_planner import GlobalRoutePlanner
from agents.navigation.basic_agent import BasicAgent

# Set up window
pygame.init()
screen = pygame.display.set_mode((640, 480))

# Connect the client and set up bp library and spawn points
client = carla.Client('localhost', 2000)
world = client.get_world()
bp_lib = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

# Clean up all other actors
for v in world.get_actors().filter('*vehicle*'):
    v.destroy()

# Select a random spawn point from the list
random_spawn_point = random.choice(spawn_points)

# Add the Hero vehicle at the random spawn point
vehicle_bp = bp_lib.find('vehicle.tesla.model3')
vehicle = world.try_spawn_actor(vehicle_bp, random_spawn_point)

# Disable all traffic lights in the world
for traffic_light in world.get_actors().filter('traffic.traffic_light'):
    traffic_light.set_state(carla.TrafficLightState.Green)  # Set to green
    traffic_light.freeze(True)  # Freeze the traffic light in its current state

# Move the spectator
spectator = world.get_spectator()

camera_mode = "first_person"  # Define


def update_camera():
    global camera_mode
    transform = vehicle.get_transform()

    if camera_mode == "first_person":
        # First-person view: Inside the car (driver's seat)
        camera_location = carla.Location(x=-0, y=-0.4, z=1.2)
        camera_rotation = transform.rotation

    elif camera_mode == "third_person":
        # Third-person view: Behind and above the car
        camera_location = carla.Location(x=-10.0, y=0.0, z=3)
        camera_rotation = transform.rotation

    spectator_transform = carla.Transform(transform.transform(camera_location), camera_rotation)
    spectator.set_transform(spectator_transform)


def toggle_camera_mode():
    global camera_mode
    if camera_mode == "first_person":
        camera_mode = "third_person"
        print(f"Switched to third-person view")
    else:
        camera_mode = "first_person"
        print(f"Switched to first-person view")


# Wait for the vehicle to spawn
time.sleep(1)

agent = BasicAgent(vehicle)

# Set a target speed for the agent (in km/h)
agent.set_target_speed(40)
agent.follow_speed_limits = True

# Define the road destination (gas station on the road)
destination_road = carla.Transform(
    carla.Location(x=-29.626791, y=-27.212812, z=0.198394),
    carla.Rotation(pitch=-0.076778, yaw=2.117271, roll=-0.002625)
)

# Define the new entrance to the parking lot
entrance = carla.Transform(
    carla.Location(x=-44.137066, y=-21.434694, z=0.054097),  # Updated entrance location
    carla.Rotation(pitch=0.002063, yaw=-90.850952, roll=0.000032)
)

# Define the parking spot inside the lot
parking_spot = carla.Location(x=-33.0, y=-30.0, z=0.198394)  # Exact parking spot coordinates

# Set the agent's destination (on-road)
agent.set_destination(destination_road.location)

# Drive the vehicle to the road destination
reached_entrance = False
reached_parking = False
while True:
    update_camera()

    # Check for 'C' key press to toggle camera mode
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Press 'C' to toggle views
                toggle_camera_mode()

    # Calculate distance to the road destination and entrance
  #  distance_to_destination_road = vehicle.get_location().distance(destination_road.location)
    distance_to_entrance = vehicle.get_location().distance(entrance.location)

    # Step 1: Autopilot until reaching the entrance
    if distance_to_entrance > 5:
        control_command = agent.run_step()
        vehicle.apply_control(control_command)

        # Step 2: Stop at the entrance and initiate turning
        if distance_to_entrance < 6.0:  # Stop at the entrance
            print(f"Reached the entrance. Stopping the vehicle...")
            vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))  # Full stop
            reached_entrance = True

            if reached_entrance and not reached_parking:
                #print(f"Performing right turn into the parking lot...")
                    
                # Gradual steering right (smooth right turn) 
                # - Reducing the max steer value and incrementally turning
                vehicle.apply_control(carla.VehicleControl(throttle=0.2, steer=0.3))  # Smooth right
                    
                # Move towards parking spot after turning
                vehicle_location = vehicle.get_location()
                distance_to_parking = vehicle_location.distance(parking_spot)
    
                # Step 3: Perform a gradual right turn into the parking lot
                if reached_entrance and not reached_parking:
                    print(f"Performing right turn into the parking lot...")
                            
                    # Gradual steering right (smooth right turn) 
                    # - Reducing the max steer value and incrementally turning
                    vehicle.apply_control(carla.VehicleControl(throttle=0.2, steer=0.3))  # Smooth right
                            
                    # Move towards parking spot after turning
                    vehicle_location = vehicle.get_location()
                    distance_to_parking = vehicle_location.distance(parking_spot)

                    if distance_to_parking > 0: #0.5 works
                        # Proportional navigation to parking spot
                        direction = parking_spot - vehicle_location
                        direction_norm = direction.make_unit_vector()

                        # Simple control for driving straight to the parking spot
                        vehicle.apply_control(carla.VehicleControl(throttle=0.3, steer=direction_norm.y * 0.5))
                   # else:
                       # reached_parking = True
                        #print(f"Arrived at the parking spot!")
                       # vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))  # Full stop

    ## Step 4: Stop once parked
    elif reached_parking:
        break

# Move the spectator to view the vehicle at the parking spot
spectator_transform = carla.Transform(
    carla.Location(x=parking_spot.x, y=parking_spot.y + 20, z=19),
    carla.Rotation(pitch=-30, yaw=0, roll=0)
)
spectator.set_transform(spectator_transform)
