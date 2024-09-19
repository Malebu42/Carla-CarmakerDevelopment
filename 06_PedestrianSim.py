#!/usr/bin/python

import carla
import math
import random
import time
import cv2 #to work with images from cameras
import numpy as np #in this example to change image representation - re-shaping

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

try:
    import queue
except ImportError:
    import Queue as queue

class CarlaSyncMode(object):
    def __init__(self, world, *sensors, fps=30):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / fps
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data


def main():
    # CARLA client and world initialization
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    # Create pedestrian and controller
    actor_list = []

    try:
        # Set synchronous mode using CarlaSyncMode
        with CarlaSyncMode(world) as sync_mode:
            world.set_pedestrians_seed(1235)

            # Spawn pedestrian
            pedestrian_bp = random.choice(world.get_blueprint_library().filter("walker.pedestrian.*"))
            spawn_location = world.get_random_location_from_navigation()

            # Debug: Check if a valid spawn location is found
            if spawn_location is None:
                print("Failed to find a valid spawn location for pedestrian")
            else:
                print(f"Spawn location found at: {spawn_location}")

            if spawn_location is not None:
                pedestrian_transform = carla.Transform(spawn_location)
                pedestrian = world.try_spawn_actor(pedestrian_bp, pedestrian_transform)

                # Debug: Check if pedestrian was spawned
                if pedestrian is None:
                    print("Failed to spawn pedestrian.")
                else:
                    print(f"Pedestrian spawned at: {pedestrian_transform.location}")
                    actor_list.append(pedestrian)

                    # Spawn walker controller
                    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
                    controller = world.try_spawn_actor(walker_controller_bp, carla.Transform(), pedestrian)

                    # Debug: Check if controller was spawned
                    if controller is None:
                        print("Failed to spawn pedestrian controller.")
                    else:
                        print(f"Controller spawned for pedestrian.")
                        actor_list.append(controller)
                        controller.start()

                        # Give the controller some time to initialize
                        time.sleep(1)  # Wait a bit before issuing movement

                        # Set destination for pedestrian to walk to
                        target_location = world.get_random_location_from_navigation()

                        if target_location is None:
                            print("Failed to find a valid target location for pedestrian.")
                        else:
                            print(f"Pedestrian moving to: {target_location}")
                            controller.go_to_location(target_location)
                            controller.set_max_speed(1.7)

                        while True:
                            # Keep updating the simulation
                            sync_mode.tick(timeout=2.0)
                            time.sleep(0.05)

    finally:
        print('Cleaning up actors...')
        for actor in actor_list:
            actor.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')