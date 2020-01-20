# Raspberry Pi Graphical Temperature Logger V1.0, Markus Jochim, Troy, Michigan, 01/2020
# https://github.com/MarkusJochim/Pi-Graphical-Temperature-Logger

import matplotlib
import constant
import os
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import logging as log
from matplotlib.gridspec import GridSpec

matplotlib.use('Agg')


def write_9am_9pm_csv_files(t_current):
    df_aggr = None

    am_pm = ['am', 'pm']
    am_pm_ptr = 0
    df_9am = df_9pm = None
    timespan = [[8, 7, 6, 5, 4, 3, 2, 1, 0, 23, 22, 21], [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9]]
    yesterday = t_current - dt.timedelta(days=1)

    for ts in timespan:
        for h1 in ts:
            if h1 >= 21 and h1 <= 23:
                folder = yesterday.strftime("%Y-%m-%d")
            else:
                folder = t_current.strftime("%Y-%m-%d")

            file = folder + os.sep + str(h1) + '.csv'
            if os.path.exists(file):
                df_next = pd.read_csv(file)
                if df_aggr is None:
                    df_aggr = df_next
                else:
                    df_aggr = df_next.append(df_aggr)
            else:
                log.info('Method \'write_9am_9pm_csv_files(t_current)\': File %s not found. Note: This may very well be '
                         'OK, if the Raspberry Pi Graphical Temperature Logger was started at a time later than the '
                         'time indicated by this filename.', file)

        if not df_aggr is None:
            data_file = t_current.strftime("%Y-%m-%d") + os.sep + '9' + am_pm[am_pm_ptr] + '_Data.csv'
            log.debug('Writing all 9 %s Data into a file: %s', am_pm[am_pm_ptr], data_file)
            df_aggr.to_csv(data_file, encoding='utf-8', index=False)

            if am_pm_ptr == 0:
                df_9am = data_file
            else:
                df_9pm = data_file
        else:
            log.info('Method \'write_9am_9pm_csv_files(t_current)\': No 9 %s data file was written. '
                     'DataFrame was None.', am_pm[am_pm_ptr])

        df_aggr = None
        am_pm_ptr += 1

    return [df_9am, df_9pm]



def generate_diagram(t_current, data_files, diag_titles, diag_filename, errFlag):
    fig = plt.figure(constrained_layout=True, figsize=(16, 9))
    gs = GridSpec(2, 1, figure=fig)
    axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0])]

    for data_file, diag_title, ax, i in zip(data_files, diag_titles, axs, [0, 1]):
        if not(data_file is None):
            df = pd.read_csv(data_file, index_col='matplotlib_date')
            df.pop('year')
            df.pop('month')
            df.pop('day')
            df.pop('hour')
            df.pop('minute')
            df.pop('second')
            df.plot(ax=ax)
        else:
            ax.text(x=0.5, y=0.5, s='No temperature data available for this time period.', color='grey',
                       alpha=0.35, fontsize=28, horizontalalignment='center', verticalalignment='center')

        if errFlag:
            loc = ['left', 'right']
            msg = "An error occurred. Search log file \'{}\' for entries tagged as \'ERROR\' " \
                  "for more information.".format(constant.LOG_FILE)
        else:
            # No error, so put the title in the center. The error message that technically goes
            # to the right is empty and therefore doesn't matter.
            loc = ['center', 'right']
            msg = ''

        ax.set_title(diag_title, color='blue', style='oblique', fontsize=14, loc=loc[0])
        ax.set_title(msg, color='red', style='oblique', fontsize=14, loc=loc[1])

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.grid(color='grey', linestyle=':', linewidth=0.4)

        if not(data_file is None):
            if i == 0:
                yesterday = t_current -  dt.timedelta(days=1)
                low = mdates.date2num(dt.datetime(yesterday.year, yesterday.month, yesterday.day, 21))
                high = mdates.date2num(dt.datetime(t_current.year, t_current.month, t_current.day, 9))
                ax.set_xlim(low, high)
            else:
                low = mdates.date2num(dt.datetime(t_current.year, t_current.month, t_current.day, 9))
                high = mdates.date2num(dt.datetime(t_current.year, t_current.month, t_current.day, 21))
                ax.set_xlim(low, high)

        xa = ax.get_xaxis()
        xa.set_label_text("Time")
        ma_x_form = mdates.DateFormatter('%H:%M')
        xa.set_major_formatter(ma_x_form)
        ma_x_loc = mdates.MinuteLocator(interval=30)
        xa.set_major_locator(ma_x_loc)
        mi_x_loc = mdates.MinuteLocator(interval=10)
        xa.set_minor_locator(mi_x_loc)

        ya = ax.get_yaxis()
        ya.set_label_text("Celsius")
        ma_y_form = ticker.StrMethodFormatter('{x:.2f}')
        ya.set_major_formatter(ma_y_form)
        ma_y_loc = ticker.LinearLocator(numticks=20)
        ya.set_major_locator(ma_y_loc)
        mi_y_loc = ticker.LinearLocator(numticks=39)
        ya.set_minor_locator(mi_y_loc)

    plt.savefig(diag_filename)
    plt.close('all')
    log.info("Diagram written to file system: %s", diag_filename)

