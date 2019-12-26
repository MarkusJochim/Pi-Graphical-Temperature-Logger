# Raspberry Pi Graphical Temperature Logger V1.0, Markus Jochim, Troy, Michigan, 01/2020
# https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger

import logging

# Paths
SENSOR_DIR = '/sys/bus/w1/devices/'
SENSOR_SLAVE = '/w1_slave'

# This should be set to "MASCHINE = 'Pi'" all the time!
# Only reason to set this to a different value (e.g. "Windows") is that that enables working on 
# source code on a different machine / OS. In that case everything that relies on the actual Pi with
# connected sensor will be 'simulated' (e.g. by not using actual sensor reads but instead reading some fake
# value from a list of values).
MASCHINE = 'Pi'

# All sensors connected must be listed in the following dictionary
# You need to replace the values below with the unique sensor IDs of the sensors connected to your Pi.
# When in doubt:
# Read instructions on https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger
SENSOR = {'S0': '28-030497796414',
          'S1': '28-03049779ce67',
          'S2': '28-0304977984d7',
          'S3': '28-03019779549c',
          'S4': '28-03019779690a'
          }

# Non-zero correction values can be applied to each temperature read taken from a sensor before storing and processing
# the measured temperature to compensate for sensor inaccuracies. Read the description of the calibration procedure
# on GitHub to understand how to set the correction values.
# Each correction value is added to a temperature value read from a sensor.
# For example: Assume 'S3' is set to -0.1335 and the temperature value read from S3 is 23 degrees celsius.
# In that case the corrected value that is stored and processed is 23+(-0.1335)=22.8665 degrees celsius.
# When in doubt of how to determine which values to use:
# Read instructions on https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger
CORRECTION_VALUE = {'S0': 0, 'S1': 0, 'S2': 0, 'S3': 0, 'S4': 0}
#
# Ignore the following line. These are my correction values which I leave here so that I can easily activate them.
# CORRECTION_VALUE = {'S0': -0.0396, 'S1': 0.471, 'S2': 0.2518, 'S3': -0.1335, 'S4': -0.5497}


# When checking which sensors are present, the code assumes that all sensor names start with the following prefix
SENSOR_PREFIX = '28-*'

# From each temperature sensor connected, the temperature value will be read every SENSOR_READ_RATE seconds.
# Recommended value that will result in nice diagrams: 30
SENSOR_READ_RATE = 30

# File to which logging messages will be written
LOG_FILE = 'log_messages.txt'

# Set to one of the following logging levels: DEBUG, INFO, ERROR
# If logging level is set to DEBUG, the LOG_FILE can become very large over time.
# Recommended level during normal operation: INFO
LOG_LEVEL = logging.INFO

# When a sensor read fails, how many attempts to read the sensor again will be taken before stop trying and
# reporting an error? Recommended value: 3
READ_ATTEMPTS = 3