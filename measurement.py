# Raspberry Pi Graphical Temperature Logger V1.0, Markus Jochim, Troy, Michigan, 01/2020
# https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger


import os
import glob
import time
import constant
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates
import logging as log


class Measurements:
    current_hour_of_the_day = None
    mockup_pointer = -1

    @staticmethod
    def sensors_present(err):
        sensors_prsnt = []; s_names = []; s_cnt = 0

        if constant.MASCHINE == 'Pi':
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            sens_prsnt_w_path = glob.glob(constant.SENSOR_DIR + constant.SENSOR_PREFIX)

            # Strip of pathnames from list elements in sensors_present
            for fi in sens_prsnt_w_path:
                sensors_prsnt.append(os.path.basename(fi))

            # Checking which of the sensors configured in 'constant.py' were present when Raspberry Pi was started
            for key in constant.SENSOR:
                if constant.SENSOR[key] in sensors_prsnt:
                    s = 'Sensor {} detected.'.format(key)
                    s_cnt += 1
                    log.info(s)
                else:
                    s = 'Sensor {} not found error.'.format(key)
                    log.error(s)
                    err = True
                
                s_names.append(s)

        return s_names, s_cnt, err
    

    @classmethod
    def startup(cls):
        # The following code ensure that, independently of when the ThermoPi starts,
        # the first sensor reads will always be aligned with the start of a minute.
        cls.t_now = dt.datetime.now()
        cls.t_now_without_seconds = dt.datetime(cls.t_now.year, cls.t_now.month, cls.t_now.day, cls.t_now.hour,
                                                cls.t_now.minute)
        cls.t_start = cls.t_now_without_seconds + dt.timedelta(minutes=2)
        cls.t_current = cls.t_start
        cls.just_started_flag = True


    @staticmethod
    def read_temperature(sensor_id, err):
        sensor_data = ['none','none']
        success = False
        celsius = -1000  # About 726.85 degrees below absolute zero ;-)
        file = constant.SENSOR_DIR + constant.SENSOR[sensor_id] + constant.SENSOR_SLAVE

        for cnt in range(constant.READ_ATTEMPTS):
            try:
                f = open(file, 'r')
                sensor_data = f.readlines()
                f.close()
            except FileNotFoundError:
                s = 'Method \'read_temperature(cls, sensor_id, err)\' raised a FileNotFoundError by attempting ' \
                    'to open or close file {}. sensor_id: {}'.format(file, sensor_id)
                log.error(s)
                err = True

            # Example of what 'sensor_data' should look like:
            # ['5a 01 55 05 7f a5 81 66 39 : crc=39 YES\n', '5a 01 55 05 7f a5 81 66 39 t=21625\n']
            # Now going to parse it...
            l0 = len(sensor_data[0])
            
            if sensor_data[0][l0-4:l0-1] == 'YES':
                pos = sensor_data[1].find('t=')
                if pos != -1:
                    s_celsius = sensor_data[1][pos+2:]
                    celsius = (float(s_celsius) / 1000.0) + constant.CORRECTION_VALUE[sensor_id]
                    success = True
                    break
            
            if (success == False):
                if (cnt+1 < constant.READ_ATTEMPTS):
                    log.info("Attempt to read valid temperature information from sensor {} failed {} times in a row. "
                             "Script will try again to read the temperature information from the sensor. In case "
                             "maximum allowed number of subsequent failed attempts (= {}) (as defined by "
                             "READ_ATTEMPTS in \'constant.py\') will be reached, an "
                             "ERROR will be reported in this log file. Information read "
                             "from sensor (if any): {}".format(sensor_id, cnt+1, constant.READ_ATTEMPTS, sensor_data))
                else:
                    log.error("Attempts to read valid temperature information from sensor {} failed too many times "
                              "in a row (= {} times) and thereby reached the maximum allowed number of "
                              "subsequent failed attempts (= {}) as defined by READ_ATTEMPTS "
                              "in \'constant.py\'. Information read from sensor "
                              "(if any): {}".format(sensor_id, cnt+1, constant.READ_ATTEMPTS, sensor_data))
                    
            time.sleep(0.2)

        err = err or (not success)
        return celsius, err


    @classmethod
    def measure_for_an_hour(cls, err):
        cls.current_hour_of_the_day = hour = cls.t_current.hour

        df = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second', 'matplotlib_date'])
        for key in constant.SENSOR:
            df[key] = pd.Series()

        while hour == cls.current_hour_of_the_day:
            if not cls.just_started_flag:
                df = df.append(cls.data, ignore_index=True)
                cls.t_current = cls.t_current + dt.timedelta(seconds=constant.SENSOR_READ_RATE)

            cls.data = {'year': cls.t_current.year, 'month': cls.t_current.month, 'day': cls.t_current.day,
                        'hour': cls.t_current.hour, 'minute': cls.t_current.minute, 'second': cls.t_current.second,
                        'matplotlib_date': mdates.date2num(cls.t_current)}

            sleep_duration = (cls.t_current - dt.datetime.now()).total_seconds()
            log.debug('sleep_duration is %ss', sleep_duration)

            if constant.MASCHINE == 'Pi':
                try:
                    time.sleep(sleep_duration)
                except ValueError:
                    s = 'Method \'measure_for_an_hour(cls)\' raised a ValueError by attempting ' \
                        'to go to sleep for an invalid duration: {}s.'.format(sleep_duration)
                    log.error(s)
                    err = True

            for key in constant.SENSOR:
                if constant.MASCHINE == 'Pi':
                    celsius, err = Measurements.read_temperature(key, err)
                else:
                    celsius, err = Measurements.read_temp_mockup(err)

                cls.data[key] = celsius
                log.debug('Measured temperature:  Sensor %s Temperature %s C', key, celsius)
                cls.just_started_flag = False

            hour = cls.t_current.hour

        return cls.t_current, df, err


    @classmethod
    def write_hourly_csv_file(cls, df):
        # Write csv files every hour on the hour
        if cls.current_hour_of_the_day == 23:  # Bit of a hack... but it works.
            t_tmp = cls.t_current - dt.timedelta(seconds=constant.SENSOR_READ_RATE)
        else:
            t_tmp = cls.t_current

        folder = t_tmp.strftime("%Y-%m-%d")

        if not os.path.isdir(folder):
            os.mkdir(folder)

        file = folder + os.sep + str(cls.current_hour_of_the_day) + '.csv'
        # If file exists, then delete. Could be 'old' and from a previous script run within same hour.
        # But this may deserve a logging output to log that a file was deleted.
        if os.path.exists(file):
            os.remove(file)
            s = 'When attempting to create file named \'{}\' an old csv file with the same name was found. ' \
                'The old file was deleted and the new one created. The old file may have been created during ' \
                'an earlier run of PiGraphicalTemperatureLogger on the same day.'.format(file)
            log.info(s)

        log.debug('Writing csv file: %s', file)
        df.to_csv(file, encoding='utf-8', index=False)



    @classmethod
    def read_temp_mockup(cls, err):
        # read_temp_mockup() is called only if constant.MASCHINE != Pi.
        # In that case the method generates some mockup sensor data.
        n_s = len(constant.SENSOR)

        values = [22.0] * (n_s * 300) + [22.125] * (n_s * 220) + [22.50] * (n_s * 400) + [22.75] * (n_s * 500) + [22.25] * (n_s * 250)
        le = len(values)-(n_s * 70)


        cls.mockup_pointer += 1
        if cls.mockup_pointer == le:
            cls.mockup_pointer = 0

        v = values[cls.mockup_pointer + (cls.mockup_pointer % n_s) * 70] + (cls.mockup_pointer % n_s) * 0.125
        return v, err

