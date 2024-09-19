#!/usr/bin/python

import carla
import math
import random
import time
import numpy as np
import cv2

client = carla.Client('localhost', 2000) 
world = client.get_world()

bp_lib = world.get_blueprint_library()
spawn_points = world.get_map().get_spawn_points()

vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020')
vehicle = world.try_spawn_actor(vehicle_bp, random.choice(spawn_points)) #specific point spawn_points[0]


spectator = world.get_spectator()
transform= carla.Transform(vehicle.get_transform().transform(carla.Location(x=-4,z=-2)),vehicle.get_transform().rotation)
spectator.set_transform(transform) #set the spectator position to the car position

camera_bp = bp_lib.find('sensor.camera.rgb')
camera_init_trans = carla.Transform(carla.Location(z=2))
camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=vehicle)

def camera_callback(image, data_dict):
    data_dict['image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))

image_w = camera_bp.get_attribute("image_size_x").as_int()
image_h = camera_bp.get_attribute("image_size_y").as_int()

camera_data = {'image': np.zeros((image_h, image_w, 4))}

camera.listen(lambda image: camera_callback(image, camera_data))


vehicle.set_autopilot(True)

cv2.namedWindow('RGB Camera', cv2.WINDOW_AUTOSIZE)
cv2.imshow('RGB Camera', camera_data['image'])
cv2.waitKey(1)

while True:
    cv2.imshow('RGB Camera', camera_data['image'])

    world.tick()

    if(cv2.waitKey(1) == ord('q')):
        break

cv2.destroyAllWindows()

''' Test if the Camera is created right
time.sleep(2)
spectator.set_transform(camera.get_transform())
camera.destroy()
'''
