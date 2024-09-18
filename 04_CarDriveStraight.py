#!/usr/bin/python

import carla
import math
import random
import time
import cv2 #to work with images from cameras
import numpy as np #in this example to change image representation - re-shaping

client = carla.Client('localhost', 2000) #client

world = client.get_world() #gets world
bp_lib = world.get_blueprint_library() #gets all vehicles
spawn_points = world.get_map().get_spawn_points() #get all spawn points
spectator = world.get_spectator() #get spectator

vehicle_bp = bp_lib.find('vehicle.tesla.model3') #vehicle.tesla.model3 to get blue car
start_point = spawn_points[0] #select first spawn point

vehicle = world.try_spawn_actor(vehicle_bp, start_point) #spawn Car at start point
print("Starting Position:", start_point) #print start point coords

spectator_pos = carla.Transform(start_point.location + carla.Location(x=20,y=10,z=4),
                                carla.Rotation(yaw = start_point.rotation.yaw -155))

spectator.set_transform(spectator_pos)

#Check if the vehicle was spawned
if vehicle is not None:
    print("Vehicle spawned at:", start_point.location)
    
else:
    print("Vehicle could not be spawned. Please check spawn point and try again.")

#camera mount offset on the car - you can tweak these to have the car in view or not
CAMERA_POS_Z = 3 
CAMERA_POS_X = -5 

camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '1500') # this ratio works in CARLA 9.14 on Windows
camera_bp.set_attribute('image_size_y', '1000')

camera_init_trans = carla.Transform(carla.Location(z=CAMERA_POS_Z,x=CAMERA_POS_X))
#this creates the camera in the sim
camera = world.spawn_actor(camera_bp,camera_init_trans,attach_to=vehicle)

def camera_callback(image,data_dict):
    data_dict['image'] = np.reshape(np.copy(image.raw_data),(image.height,image.width,4))

image_w = camera_bp.get_attribute('image_size_x').as_int()
image_h = camera_bp.get_attribute('image_size_y').as_int()

camera_data = {'image': np.zeros((image_h,image_w,4))}
# this actually opens a live stream from the camera
camera.listen(lambda image: camera_callback(image,camera_data))
 
# define speed contstants
PREFERRED_SPEED = 30 # what it says
SPEED_THRESHOLD = 2 #defines when we get close to desired speed so we drop the

#adding params to display text to image
font = cv2.FONT_HERSHEY_SIMPLEX
# org - defining lines to display telemetry values on the screen
org = (30, 30) # this line will be used to show current speed
org2 = (30, 50) # this line will be used for future steering angle
org3 = (30, 70) # and another line for future telemetry outputs
org4 = (30, 90) # and another line for future telemetry outputs
org3 = (30, 110) # and another line for future telemetry outputs
fontScale = 0.5
# white color
color = (255, 255, 255)
# Line thickness of 2 px
thickness = 1

def maintain_speed(s):

    #s arg is actual current speed 
    if s >= PREFERRED_SPEED:
        return 0
    elif s < PREFERRED_SPEED - SPEED_THRESHOLD:
        return 0.8 # think of it as % of "full gas"
    else:
        return 0.4 # tweak this if the car is way over or under preferred speed 

# - press Q to exit, you need to run the bit above to start the car

cv2.namedWindow('RGB Camera',cv2.WINDOW_AUTOSIZE) # create new window for behind car camera
cv2.imshow('RGB Camera',camera_data['image'])

#main loop 
quit = False

while True:
    # Carla Tick
    world.tick()
    if cv2.waitKey(1) == ord('q'):
        quit = True
        break
    image = camera_data['image']
    
    steering_angle = 0 # we do not have it yet
    # to get speed we need to use 'get velocity' function
    v = vehicle.get_velocity()
    # if velocity is a vector in 3d
    # then speed is like hypothenuse in a right triangle
    # and 3.6 is a conversion factor from meters per second to kmh
    # e.g. kmh is 1000 meters and one hour is 60 min with 60 sec = 3600 sec
    speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
    # now we add the speed to the window showing a camera mounted on the car
    image = cv2.putText(image, 'Speed: '+str(int(speed))+' kmh', org2, 
                        font, fontScale, color, thickness, cv2.LINE_AA)
    # this is where we used the function above to determine accelerator input
    # from current speed
    estimated_throttle = maintain_speed(speed)
    # now we apply accelerator
    vehicle.apply_control(carla.VehicleControl(throttle=estimated_throttle, 
                                               steer=steering_angle))
    cv2.imshow('RGB Camera',image)

#clean up
cv2.destroyAllWindows()
camera.stop()
for actor in world.get_actors().filter('*vehicle*'):
    actor.destroy()
for sensor in world.get_actors().filter('*sensor*'):
    sensor.destroy()
