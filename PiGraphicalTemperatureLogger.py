# Raspberry Pi Graphical Temperature Logger V1.0, Markus Jochim, Troy, Michigan, 01/2020
# https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger


import time
import os
import constant
import datetime as dt
import visualize as vs
import logging as log
from measurement import Measurements
from concurrent.futures import ThreadPoolExecutor

# Configure logging mechanism
log.basicConfig(filename=constant.LOG_FILE, level=constant.LOG_LEVEL, filemode='a',
                format='%(asctime)s - %(levelname)s - %(message)s')

# tdys_err is set to 'True' when a log
# entry of log level 'ERROR' is created.
# tdys_err is reset to 'False' every day at 9pm.
tdys_err = False

start_msg = 'Raspberry Pi Graphical Temperature Logger started.'
log.info(start_msg)

print("\nRaspberry Pi Graphical Temperature Logger V1.0:\n")
print("The logger will...")
print("  - write temperature measurement data as .csv files to the file system every hour on the hour.")
print("    .csv files can be opened with e.g. Excel, Libre Office Calc or text editors.")
print("  - write a jpg diagram to the file system that visualizes all measurements on a daily basis at 9pm.")
print("\nNote:")
print("  - All files will be written to the current working directory: {}".format(os.getcwd()))
print("  - Log messages will be written to \'{}\' as per the LOG_FILE and LOG_LEVEL settings "
      "in \'constant.py\'.".format(constant.LOG_FILE))
print("  - The Temperature Logger will continue running \"forever\". "
      "Once you have all measurements/files you need, simply abort execution.\n")

s_names, s_cnt, tdys_err = Measurements.sensors_present(tdys_err)
[print(i) for i in s_names]
print("\nTotal of {} connected sensors detected.".format(s_cnt, s_names))
print("\nRunning...")


Measurements.startup()

while True:
    t_current, df, tdys_err = Measurements.measure_for_an_hour(tdys_err)
    h = t_current.hour

    if constant.MASCHINE != 'Pi':
        time.sleep(0.2)

    Measurements.write_hourly_csv_file(df)

    if h == 21:
        errFlag = tdys_err
        tdys_err = False
        data_file_names = vs.write_9am_9pm_csv_files(t_current)
        diag_filename = (t_current - dt.timedelta(days=1)).strftime("%Y_%m_%d_to_") + \
                        t_current.strftime("%Y_%m_%d") +'_Diagram.jpg'
        diag1_title = (t_current - dt.timedelta(days=1)).strftime("%m/%d/%Y, 9:00 pm - ") + \
                      t_current.strftime("%m/%d/%Y, 9:00 am")
        diag2_title = t_current.strftime("%m/%d/%Y, 9:00 am - %m/%d/%Y, 9:00 pm")
        diag_titles = [diag1_title, diag2_title]

        if constant.MASCHINE == 'Pi':
            pool = ThreadPoolExecutor()
            future = pool.submit(vs.generate_diagram, t_current, data_file_names, diag_titles, diag_filename, errFlag)
        else:
            vs.generate_diagram(t_current, data_file_names, diag_titles, diag_filename, errFlag)
