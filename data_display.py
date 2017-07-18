# -*- coding: utf-8 -*-
# !/usr/bin/env python

__author__ = 'berniey'

import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from util import traffic_decimal
from data import DataCore


class DataDisplay(object):

    def __init__(self):
        pass

    def _drawing(self, data, kind, use_index, xlabel, ylabel, line_color,
                      fig_color, funciton, x_str, y_str, title, figsize):
        self._construct_figure(figsize=figsize)
        self._construct_guideline_avg(data, color=line_color)
        self._construct_axe(data, funciton)
        self._chose_graphic_kind(data, kind=kind, use_index=use_index, xlabel=xlabel,
                                 ylabel=ylabel, color=fig_color,
                                 x_str=x_str, y_str=y_str, title=title
                                 )
        plt.show()

    def _construct_figure(self, figsize):
        self.fig, self.ax0 = plt.subplots(figsize=figsize)
        plt.subplots_adjust()

    def _construct_guideline_avg(self, data, color):
        # 添加一条显示平均数的辅助线
        avg = data.mean()
        self.ax0.axvline(x=avg, color=color,
                         label='Average', linestyle='--',
                         linewidth=1
                         )

    def _construct_axe(self, data, funciton):
        # 坐标轴的长度
        self.ax0.set_xlim([0, 10 ** len(str(data.max()))])
        # 设置title和label

        # 函数，改变x轴的单位
        if funciton:
            formatter = FuncFormatter(funciton)
            self.ax0.xaxis.set_major_formatter(formatter)

    def _chose_graphic_kind(self, data, kind, use_index, xlabel, ylabel, color, x_str, y_str, title):
        self.ax0.set(title=title, xlabel=xlabel, ylabel=ylabel)
        print(data)
        data.plot(kind=kind, color=color, ax=self.ax0, use_index=use_index, fontsize=10, secondary_y=False)

    def show_graphic(self, data, kind, use_index, xlabel, ylabel, line_color,
                     fig_color, funciton, x_str, y_str, title, figsize):

        self._drawing(data, kind, use_index, xlabel, ylabel, line_color,
                      fig_color, funciton, x_str, y_str, title, figsize)


if __name__ == '__main__':
    d = DataCore()
    d.generate_data()
    d.get_url_traffic_data()
    dd = DataDisplay(d)
