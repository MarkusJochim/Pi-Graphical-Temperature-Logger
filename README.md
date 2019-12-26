# Pi-Graphical-Temperature-Logger
A Python based Graphical Temperature Logger for the Raspberry Pi

_Last updated 12/26/2019_

# Table of Contents

1. Overview
1. Temperature Sensors
1. Preparing your Raspberry Pi
1. Running the Temperature Logger
1. Tweaking Settings to your liking (Optional Step)
1. Sensor calibration and correction values (Optional Step)

![Hardware used](/images/Hardware.jpg)

# Overview

This tutorial explains how to turn your Raspberry Pi into a graphical temperature logger for long term temperature logging and visualization. We will go over how to hook up the Pi to some affordable temperature sensors and how to install and run the temperature logger software.

In a nutshell the logger will:

* Write temperature measurement data as .csv files every hour on the hour.<br>
(.csv files can opened with Excel, Libre Office Calc, text editors and other tools.)
* Write a jpg that visualizes 24 hours of logged temperature data every day at 9pm. 

Once started the logger will essentially run ‘forever’ and the execution can simply be aborted once all required files (.csv and/or jpg) are available.

I created the Temperature Logger as my little ‘2019 Christmas break project’ and I hope you will enjoy it.  (Markus Jochim - 12/2019).

![Measurement Example](/images/2019_12_22_to_2019_12_23_Diagram.jpg)

# Temperature Sensors

I ordered five DS18b20 sensors and got them for about $2.6 a piece. These sensors can be easily found online. They have an operating temperature range of -55 to +125 degrees Celsius and accuracy of +/- 0.5 degrees Celsius over the range of -10 to +85 degrees Celsius. The ones I bought are waterproof and have a cable length of 2 meters. Since these have three wires (red (VCC), black (GND), yellow (Data)) I decided to simply solder these on to 3.5 mm audio connectors. I also bought 5 matching female stereo jack panel mount connectors.

![Sensor and Connector](/images/Sensor_and_Connector.jpg)

This is how you connect the sensors to the Raspberry Pi. You need a 4.7 kΩ resistor between VCC and Data.

![Circuit](/images/circuit.jpg)

I decided to put hide this really simple circuit in an old conduit box that I still had in my basement. You can see that I labeled each sensor with names from S0 to S4. I recommend you do the same as these sensor names will occur a couple of more times in this tutorial as well as during script configuration.

![Conduit_Box](/images/Box_1.jpg)

In the back you can see that there is one additional Audio Jack from which three jumper wires (black, red and yellow) run to the Raspberry pi and connect to pins 1, 4 and 7, as per the diagram above.

# Preparing your Raspberry Pi

**Python Libraries:**
I use Python 3.7.3 on a Raspberry Pi running Raspbian (OS version: Buster). The Python script uses a few libraries. The ones worth mentioning are Pandas (version 0.23.3) which I use for managing tabular data and Matplotlib (version 3.0.2) for visualizing the temperature measurements. I haven’t done much testing with older versions of these libraries, so I can’t tell if older versions will work just fine or not.

**1-wire protocol:**
The sensors use the so called 1-wire protocol for serial data communication. There are a few steps necessary to prepare you Pi so that is will detect the sensors and communicate with them.

* Step 1:<br>Edit `/boot/config.txt` by entering the following command: `sudo nano /boot/config.txt`<br>
* Step 2:<br>At the bottom of this file add the following line: `dtoverlay=w1-gpio`<br>
* Step 3:<br>Once you saved the file, restart you Raspberry Pi for the changes to become effective.<br>

Strictly speaking these are all the steps required to prepare you Raspberry Pi. Executing the following additional steps at the command line will allow you to do a quick test of the sensors connected to you Pi and they will also enable you to write down which sensor (S0 to S4) has which sensors ID. This information will be required when configuring the script later on.

* Step 4:<br>Enter<br>`sudo modprobe w1-gpio`<br>`sudo modprobe w1-therm`<br>`cd /sys/bus/w1/devices`<br>`ls`<br><br>
* Step 5:<br>Here are the \"sensor directories\" I see after executing Step 4 on my Pi:<br>![Sensor Directories](/images/sensor_directories.jpg)<br><br>Each sensor has a unique ID (similar to a MAC address on a WiFi or Ethernet NIC) and each sensor directory is named after the unique sensor ID of one of the 5 sensors connected to my Raspberry Pi.<br><br>Now change into one of the sensor directories. For instance, in my case, through a command such as `cd 28-03019779549c`.<br><br>Then enter:`cat w1_slave`<br><br>The output you will see will look similar to what is shown below. The key information is the t=21187 shown in the screenshot. If you divide this number by 1,000 the resulting value is the measured temperature in Celsius which was 21.187 degrees.<br>![cat_w1_slave](/images/cat_w1_slave.jpg)<br><br>
* Step 6:<br>By repeating Step 5 for each sensor directory, you can get temperature reads from all connected sensors. Assuming you labeled your sensors S0 to S4 as suggested above, then now is the time to find out which sensor name (S0 to S4) maps to which sensor ID. Hold sensors S0 in your hand and check (as shown in step 5) from which sensor directory you get higher temperature reads through the `cat w1_slave` command. Once you found out which sensor directory represents S0, write that information down and repeat the process for sensors S1 to S4.



    
    


