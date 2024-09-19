#!/usr/bin/python

import carla 
import math 
import random 
import time 
import cv2
import open3d as o3d
from matplotlib import cm
from dataclasses import dataclass
from cyclonedds.domain import DomainParticipant
from cyclonedds.core import Qos, Policy
from cyclonedds.pub import DataWriter
from cyclonedds.sub import DataReader
from cyclonedds.topic import Topic
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.annotations import key
from time import sleep
import numpy as np
import os
name = f"{os.getpid()}"
obs = False

#Setting up cyclone dds:
@dataclass
class VehicleData(IdlStruct, typename="Chatter"):
    name: str
    key("name")
    message: str
    speed: float
    obstacle: bool

rng = np.random.default_rng()
dp = DomainParticipant()
tp = Topic(dp, "Hello", VehicleData, qos=Qos(Policy.Reliability.Reliable(0)))
dw = DataWriter(dp, tp)
dr = DataReader(dp, tp)

# Connect the client and set up bp library and spawn point
client = carla.Client('localhost', 2000)
world = client.get_world()
bp_lib = world.get_blueprint_library() 
spawn_points = world.get_map().get_spawn_points() 

# Add vehicle
vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020') 
vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[10])
time.sleep(1)

def process_lidar_data(data):
    global obs
   # Assuming the LiDAR data is in the form of 'carla.LidarMeasurement'
    # You may need to adapt this part based on your specific LiDAR sensor and data format.
    
    # Access the point cloud data
    point_cloud = data.raw_data
    
    # Ensure the data is not empty and has enough elements
    if len(point_cloud) % 3 == 0:
        points_in_front = False
        for point_index in range(0, len(point_cloud), 3):
            # Check if there are enough elements in the array
            if point_index + 2 < len(point_cloud):
                x = point_cloud[point_index]
                y = point_cloud[point_index + 1]
                z = point_cloud[point_index + 2]
                
                # Assuming an obstacle if a point is within a certain distance and in front of the vehicle
                if 0.0 < z < 2.0 and abs(x) < 1.5:
                    points_in_front = True
                    break
        if points_in_front:
           # print("Obstacle detected in front of the vehicle!")
            obs = True
        else:
           # print("No obstacles in front of the vehicle.")
            obs = False

#set up the sensor
lidar_bp = bp_lib.find('sensor.lidar.ray_cast')
lidar_transform = carla.Transform(carla.Location(x=1.0, z=2.0), carla.Rotation())
lidar_sensor = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

lidar_sensor.listen(process_lidar_data)

# Move spectator to view ego vehicle
spectator = world.get_spectator() 
transform = carla.Transform(vehicle.get_transform().transform(carla.Location(x=-4,z=2.5)),vehicle.get_transform().rotation) 
spectator.set_transform(transform)

vehicle.set_autopilot(True) 

while True:
    world.tick()

    #vehicle speed
    velocity = vehicle.get_velocity()
    speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5  # Convert to km/h
    rounded_speed = round(speed, 0)
    
    
    #Manage cyclone dds transfer:
    sample = VehicleData(name=name, message="Current_Vehicle_Speed", speed=rounded_speed, obstacle=obs)
    print("Writing ", sample)
    dw.write(sample)
    for sample in dr.take(10):
        print("Read ", sample)
    

    transform2 = carla.Transform(vehicle.get_transform().transform(carla.Location(x=-4,z=2.5)),vehicle.get_transform().rotation) 
    spectator.set_transform(transform2)