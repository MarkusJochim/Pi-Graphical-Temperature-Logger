# Pi-Graphical-Temperature-Logger
A Python based Graphical Temperature Logger for the Raspberry Pi

_Markus Jochim, Troy, Michigan

# Table of Contents

1. Overview
1. Temperature Sensors
1. Preparing your Raspberry Pi
1. Running the Temperature Logger
1. Tweaking Settings to your liking (optional step)
1. Sensor calibration and correction values (optional step)

![Hardware used](/images/Hardware.jpg)

# Overview

This tutorial explains how to turn your Raspberry Pi into a graphical temperature logger for long term temperature logging and visualization. We will go over how to hook up the Pi to some affordable temperature sensors and how to install and run the temperature logger software.

In a nutshell the logger will:

* Write temperature measurement data as .csv files every hour on the hour.<br>
(.csv files can opened with Excel, Libre Office Calc, text editors and other tools.)
* Write a jpg that visualizes 24 hours of logged temperature data every day at 9pm. 

Once started the logger will essentially run ‘forever’ and the execution can simply be aborted once all required files (.csv and/or jpg) are available.

I created the Temperature Logger as my little ‘2019 Christmas break coding project’ and I hope you will enjoy it.

![Measurement Example](/images/2019_12_22_to_2019_12_23_Diagram.jpg)

# Temperature Sensors

I ordered five DS18b20 sensors and got them for about $2.60 a piece. These sensors can be easily found online. They have an operating temperature range of -55 to +125 degrees Celsius and accuracy of +/- 0.5 degrees Celsius over the range of -10 to +85 degrees Celsius. The ones I bought are waterproof and have a cable length of 2 meters. Since these have three wires (red (VCC), black (GND), yellow (Data)) I decided to simply solder these on to 3.5 mm audio connectors. I also bought 5 matching female stereo jack panel mount connectors.

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
* Step 6:<br>By repeating Step 5 for each sensor directory, you can get temperature reads from all connected sensors. Assuming you labeled your sensors S0 to S4 as suggested above, then now is the time to find out which sensor name (S0 to S4) maps to which sensor ID. Hold sensors S0 in your hand to warm it up a bit and then check (as shown in step 5) from which sensor directory you get higher temperature reads through the `cat w1_slave` command. Once you found out which sensor directory represents S0, write that information down and repeat the process for sensors S1 to S4.

# Running the Temperature Logger
Download the Python files (`PiGraphicalTemperatureLogger.py`, `measurement.py`, `visualize.py` and `constant.py`) from the github repository by entering the following command:<br><br>`git clone https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger.git`<br><br>
![Clone](/images/clone.jpg)
Open the file `constant.py` with an editor and find the `SENSOR =` line. For all sensors S0 to S4 connected to your Pi, make sure to enter the correct Sensor ID as identified in Step 6 above. In case you are working with fewer or more sensors, either shorten the list accordingly, or add additional sensor names and IDs such as ‘S5’, ‘S6’, . . . Here is what things look like on my Pi based on the unique sensor ids associated with the sensors I own:![Sensor IDs](/images/sensor_ids.jpg)<br><br>
Then execute the following command:  `sudo python PiGraphicalTemperatureLogger.py`
If you have multiple versions of python installed on your Pi, then make sure that `sudo python` starts a Python 3.x interpreter (as mentioned above, I tested the code on Python 3.7.3). Also, depending on your setup, you may need no do a `sudo python3` instead of `sudo python` and depending on also depending on your Raspberry Pi setup you may or may not need the `sudo` part of the command or may be OK with just doing a `python PiGraphicalTemperatureLogger.py`.One thing you will need to make sure is that your Python interpreter can import the pandas and matplotlib libraries mentioned above!<br><br>
After entering this command, you should see an output similar to the picture below on your screen:<br>
![Logger started](/images/started.jpg)<br><br>

The script is now running. You should see a log file named `log_messages.txt` showing up in your working directory. At the end of each hour, on the hour, a .csv file with temperature measurement data will be created in a subdirectory. Also, every day at 9pm a jpg file will be created that visualizes the last 24 hours of temperature measurements.

# Tweaking Settings to your liking (optional step)
It is worth having a look at ‘constant.py’ as this file contains a couple of useful settings you can tweak to your liking. We already touched on the `SENSOR` setting. Other settings will determine things such as e.g. at what rate data is read from each sensor, what log level (`DEBUG`, `INFO` or `ERROR`) you want to apply and a few others.<br><br>
While log entries labeled `DEBUG` or `INFO` are \"harmless\", entries labeled `ERROR` aren’t. If an error occurs it will not only be logged in the log file, but also the next jpg measurement diagram created will contain a message indicating that an error occurred. If, for instance, several subsequent attempts of reading a sensor value are unsuccessful and the maximum number of attempts (as defined by `READ_ATTEMPTS`) was reached without success, then an error will be reported in the log file and in the next jpg measurement diagram created. This could for example happen in case one of the sensors is temporarily disconnected from the Raspberry Pi during script execution.<br><br>
As an aside:<br>
When the script is started, it reports which sensors listed in `constant.py` it detected and which ones were not detected (if any). The Raspberry Pi responds a bit slow to connecting and disconnecting sensors in the sense of respective sensor directories appearing / disappearing in the file system. If, for instance, a sensor S2 is disconnected, then the associated sensor directory will be visible in the file system for at least some time. Obviously, there is no way of reading values from a disconnected sensor, but the sensor may be reported as connected upon startup of the script if it was disconnected just briefly before starting the script. If a sensor is disconnected the reported default temperature for that sensor in .csv files and jpg diagrams is -1,000 degrees Celsius. If a temporarily disconnected sensor is connected back to the Pi, the script will be able to successfully continue reading temperature values from it.

# Sensor calibration and correction values (optional step)
The following diagram shows measurements that were taken without applying any correction values (we will get to these in a minute) and with all 5 sensors located at the same spot and being exposed to the same room temperature overnight. 

![Measurement Example](/images/2019_12_22_to_2019_12_23_Diagram.jpg)

Looking at the sensor data it seems that there was an almost constant offset between measurements taken by the 5 sensors throughout the night. S4 always shows a higher temperature read than all other sensors, followed by S3, S0, S2 and finally S1. I therefore decided to introduce correction values that can be applied to measurements to compensate for measurement offsets specific to a certain sensor. The following screenshot shows the correction value settings specific for the 5 sensors I own. However, when you download the code from the github repository the `CORRECTION_VALUE` you will see are all set to 0, in other words, no correction values will be applied.
![No correction values](/images/correction_zero.jpg)

Let’s take an example: As already observed the S4 sensor I own always is a bit on the high side with its temperature readings. The S4 value of -0.5497 means that this value will be added to each temperature value read from sensor S4. So if for instance a temperature of 22.375 degrees Celsius is measured, then the corrected value that is stored / processed / displayed will be 22.375 + (-0.5497) = 21.8253 degrees Celsius.
After setting `CORRECTION_VALUE` to the values shown above, I did another run with all 5 sensors located at the same spot. Here is the result:

![Measurement Example](/images/2019_12_24_to_2019_12_25_Diagram.jpg)

As you can see, the values are now much closer to one another.<br><br>
Here is how you can calculate the correction values specific to the sensors you own:<br>
* Step 1:<br>Place all your sensors next to each other and wait for a few minutes before you start the script execution so that all sensors will reach the same temperature (in case you touched them). Then run the script overnight to get measurements from 9pm to 9am on the following day. You will find the measurements in the `9am_Data.csv` the script creates for that night.<br><br>
* Step 2:<br>Use Libre Office Calc or Excel to open `9am_Data.csv`. The white columns will exist and you will need to manually add the columns / calculations shown in the green and blue areas as per the following description:<br><br>Column M contains the average of the measurements taken by S0, S1, S2, S3 and S4. Column N takes that average and subtracts the temperature measured by S0. Columns O to R do the same for sensors S1 to S4.<br>![Excel Top](/images/Excel_top.jpg)At the bottom of the table (blue area) we calculate the average over all rows for columns N to R and round the resulting values to 4 digits.<br>![Excel Bottom](/images/Excel_bottom.jpg)<br>
* Step 3:<bR>The values in row 1441 that you will get for you sensors will then need to be used in `constant.py` as the values for the `CORRECTION_VALUE` dictionary:<br>`CORRECTION_VALUE = {'S0': -0.0396, 'S1': 0.471, 'S2': 0.2518, 'S3': -0.1335, 'S4': -0.5497}`<br><br>
  
As you can tell from the calculation, there is an underlying assumption that the ‘true’ temperature value is the average of the temperatures measured by all 5 sensors. While this is not necessarily always true, the calibration step will at least accomplish that all sensors will return similar readings at the same temperature point. If you have a ‘golden sensor’ (e.g. in case you own a thermometer that is very precise), you can easily adjust calculations to not gravitate to the average of the temperature readings from all 5 sensor but to the values read from an high precision thermometer by introducing an additional offset to all 5 correction values.
