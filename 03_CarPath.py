#!/usr/bin/python
import sys
sys.path.append('/home/ubuntu/CARLA_0.9.14/PythonAPI/carla')
from agents.navigation.global_route_planner import GlobalRoutePlanner

import carla
import time

client = carla.Client('localhost', 2000)  # client
world = client.get_world()  # gets world
bp_lib = world.get_blueprint_library()  # gets all vehicles
spawn_points = world.get_map().get_spawn_points()  # get all spawn points
spectator = world.get_spectator()  # get spectator

# for navigating:
town_map = world.get_map()  # gets map
roads = town_map.get_topology()

vehicle_bp = bp_lib.find('vehicle.tesla.model3')  # get blue car
start_point = spawn_points[0]  # select first spawn point

vehicle = world.try_spawn_actor(vehicle_bp, start_point)  # spawn Car at start point
print("Starting Position:", start_point)  # print start point coords

# Traffic Manager setup
traffic_manager = client.get_trafficmanager(8000)  # Use a different port, e.g., 8001
#traffic_manager.set_synchronous_mode(True)  # Ensure synchronous mode if required

# Drawing the route
sampling_resolution = 2.0
grp = GlobalRoutePlanner(town_map, sampling_resolution)

# Define starting and ending points as carla.Location
point_a = start_point.location
point_b = carla.Location(x=-113.9, y=14.42, z=-0.0037)

# Trace the route between points
route = grp.trace_route(point_a, point_b)

# Print route to verify waypoints
if not route:
    print("No route found between point_a and point_b.")
else:
    print(f"Route found with {len(route)} waypoints.")
    #for idx, (waypoint, road_option) in enumerate(route):
        #print(f"Waypoint {idx}: {waypoint.transform.location}")

# Draw the route  with lines
    for i in range(len(route) - 1):
        loc1 = route[i][0].transform.location #startpoint
        loc2 = route[i + 1][0].transform.location #endpoint

        for offset in range(0, 1):  # drawing 3 parallel lines -1/2
            world.debug.draw_line(
                loc1,
                loc2,
                #carla.Location(loc1.x + offset * 0.1, loc1.y, loc1.z),
                #carla.Location(loc2.x + offset * 0.1, loc2.y, loc2.z), 
                color=carla.Color(r=0, g=0, b=255), 
                life_time=120.0,
                persistent_lines=True
            )

# Optional: set spectator to follow vehicle
    vehiclepos_spectator = carla.Transform(
        vehicle.get_transform().transform(carla.Location(x=-10, z=3)), 
        vehicle.get_transform().rotation
    )
    spectator.set_transform(vehiclepos_spectator)

# Keep the autopilot running
    while True: 
        #Enable autopilot
        vehicle.set_autopilot(True)

        # Optional: set spectator to follow vehicle
        vehiclepos_spectator = carla.Transform(
        vehicle.get_transform().transform(carla.Location(x=-10, z=3)), 
        vehicle.get_transform().rotation
            )   
        spectator.set_transform(vehiclepos_spectator)
        time.sleep(0.0005)

# Check if the vehicle was spawned
if vehicle is not None:
    print("Vehicle spawned at:", start_point.location)
else:
    print("Vehicle could not be spawned. Please check spawn point and try again.")


