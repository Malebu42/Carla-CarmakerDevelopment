#!/usr/bin/python

import glob
import os
import sys
import time
import random
import math
import numpy as np
import cv2
import open3d as o3d
from matplotlib import cm

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def generate_lidar_blueprint(blueprint_library):
    lidar_blueprint = blueprint_library.find('sensor.lidar.ray_cast_semantic')
    lidar_blueprint.set_attribute('channels', str(64))
    #write the code for set points_per_second
    lidar_blueprint.set_attribute("points_per_second",str(56000))
    #write the code for set rotation frequency
    lidar_blueprint.set_attribute("rotation_frequency",str(80))
    #write the code for set range
    lidar_blueprint.set_attribute("range",str(100))
    return lidar_blueprint


object_id = {"None": 0,
             "Buildings": 1,
             "Fences": 2,
             "Other": 3,
             "Pedestrians": 4,
             "Poles": 5,
             "RoadLines": 6,
             "Roads": 7,
             "Sidewalks": 8,
             "Vegetation": 9,
             "actor_vehicles": 10,
             "Wall": 11,
             "TrafficsSigns": 12,
             "Sky": 13,
             "Ground": 14,
             "Bridge": 15,
             "RailTrack": 16,
             "GuardRail": 17,
             "TrafficLight": 18,
             "Static": 19,
             "Dynamic": 20,
             "Water": 21,
             "Terrain": 22,
             "Not in List": 23,
             "Not in list": 24,
             }



key_list = list(object_id.keys())
value_list = list(object_id.values())


def semantic_lidar_data(point_cloud_data):
    distance_name_data = {}

    for detection in point_cloud_data:
        if detection.object_tag in value_list:
            # print(detection)
            position = value_list.index(detection.object_tag)
            distance = math.sqrt((detection.point.x ** 2) + (detection.point.y ** 2) + (detection.point.z ** 2))
            distance_name_data["distance"] = distance
            distance_name_data["name"] = key_list[position]
            
            #print(detection.object_tag)
            #write code here to display only name of object
            print("Name of object(s) nearby car  : - {}".format(distance_name_data['name']))
            print("Distance: - {}".format(distance_name_data['distance']))

            #Camera follow the car
            simulator_camera_location_rotation = carla.Transform(actor_vehicle.get_transform().transform(carla.Location(x=-2,z=+3)),actor_vehicle.get_transform().rotation)
            actor_vehicle_spectator = world.get_spectator()
            actor_vehicle_spectator.set_transform(simulator_camera_location_rotation)


def car_control():
   # actor_vehicle.apply_control(carla.actor_vehicleControl(throttle=0.51))
    time.sleep(20)

try:
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    map = world.get_map()
    get_blueprint_of_world = world.get_blueprint_library()
    car_model = get_blueprint_of_world.find('vehicle.lincoln.mkz_2020') 
    spawn_point = (world.get_map().get_spawn_points()[0])

    for v in world.get_actors().filter('*actor_vehicle*'): 
        v.destroy()

    actor_vehicle = world.spawn_actor(car_model, spawn_point)

    time.sleep(0.1)

    simulator_camera_location_rotation = carla.Transform(actor_vehicle.get_transform().transform(carla.Location(x=-2,z=+3)),actor_vehicle.get_transform().rotation)
    actor_vehicle_spectator = world.get_spectator()
    actor_vehicle_spectator.set_transform(simulator_camera_location_rotation)

    tm = client.get_trafficmanager(8000)

    actor_vehicle.set_autopilot(True,8000)
    #sensor stuff:
    lidar_sensor = generate_lidar_blueprint(get_blueprint_of_world)
    sensor_lidar_spawn_point = carla.Transform(carla.Location(x=0, y=0, z=2.0),carla.Rotation(pitch=0.000000, yaw=90.0, roll=0.000000))
    sensor = world.spawn_actor(lidar_sensor, sensor_lidar_spawn_point, attach_to=actor_vehicle)

    sensor.listen(lambda point_cloud_data: semantic_lidar_data(point_cloud_data))
    car_control()

    time.sleep(1000)

    
finally:
    print('destroying actors')
    print('done.')