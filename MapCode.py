#!/usr/bin/python

import carla 

# Read the .osm data
f = open("/home/ubuntu/Downloads/MapLubuCarla.osm", 'r') # Windows will need to encode the file in UTF-8. Read the note below. 
osm_data = f.read()
f.close()

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("/home/ubuntu/Downloads/MapLubuCarla.osm", 'w')
f.write(xodr_data)
f.close()