# encoding: utf-8
import matplotlib.pyplot as plt

from judge.ext.sn_eq_1_rule import SNEq1Rule
from misc import setup_axis_datetime


def plot_sne1(entries,
              figure=None, subplot_n=111,
              log_info=False, logger=None,
              y_attr='si_create_time', y_attr_name='$SI创建时间',
              show=False):
    entries = entries[entries.sn == 1].sort(columns=['id'])

    _p = logger.info if logger else print

    xs, ys, a_xs, a_ys = [], [], [], []
    for _, o in entries.iterrows():
        xs.append(o.id)
        ys.append(o[y_attr])

        if o.abnormal:
            if SNEq1Rule.conclusion in o.conclusions:
                a_xs.append(o.id)
                a_ys.append(o[y_attr])

        if log_info:
            pass

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    ax.plot(xs, ys, 'gD', linestyle='-.', label=y_attr_name)
    ax.plot(a_xs, a_ys, 'rD')

    ax.legend()
    ax.set_xlabel('MFT编号')
    ax.set_ylabel(y_attr_name)

    setup_axis_datetime(ax.yaxis)

    if show:
        plt.show(figure)

    return figure

def plot_lsn(entries,
             figure=None, subplot_n=111,
             log_info=False,
             logger=None,
             y_attr='si_create_time', y_attr_name='$SI创建时间',
             show=False):
    entries = entries.sort(columns=['lsn', 'id'])

    _p = logger.info if logger else print

    xs, ys = [], []
    for _, o in entries.iterrows():
        xs.append(o.lsn)
        ys.append(o[y_attr])

        if log_info:
            pass

    figure = figure or plt.figure()
    ax = figure.add_subplot(subplot_n)

    ax.plot(xs, ys, 'b^', linestyle='-.', label=y_attr_name)

    setup_axis_datetime(ax.yaxis)

    ax.legend()
    ax.set_xlabel('$LogFile序列号')
    ax.set_ylabel(y_attr_name)

    if show:
        plt.show(figure)

    return figure
