#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    Created by Klaus Lee on 2021/8/31
-------------------------------------------------
"""

import time
import numpy as np
import pandas as pd
import tushare as ts
import datetime
import os
import sys

ROOT_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(ROOT_PATH, 'Data')
RESULT_PATH = os.path.join(ROOT_PATH, 'Result')
pro = ts.pro_api("6144f3417ac5da6235442a7bafe9ba6931c3fba8dcdd8946d089f862")


class Strategy:
    def __init__(self, start_date, end_date, variety, freq='D', cash=1000000.0):
        """
        初始化部分，包括数据选择和初始本金、初始仓位、当前各种状态
        start_date : datetime.datetime
            策略开始日期
        end_date : datetime.datetime
            策略结束日期
        variety : str
            期货品种（这里不考虑跨品种策略）
        freq : str
            策略频率
            ‘D’ ：日频
            ‘W’ ：周频
            ‘M’ ：月频
        cash : float
            初始现金

        signal : str

        """
        self.start_date = start_date
        self.end_date = end_date
        self.variety = variety
        self.freq = freq

        self.cash = cash

        self.signal = ''
        pass

    # def special(self):
    #     """
    #     初始化非通用部分（由策略设定的变量）
    #     :return:
    #     """
    #     print('Function {0} Must be Overridden'.format('special'))
    #
    #     pass

    def get_data(self):
        """
        从数据库中选取策略所需的最小维度的数据
        开始日，结束日，策略品种，策略频率
        :return:
        """
        pass

    def signal(self):
        """
        构建策略，生成做多做空信号
        :return:

        """
        print('Function {0} Must be Overridden'.format('signal'))

    def update_status(self):
        """
        当前各种状态（每次交易和收盘后都更新）
        :return:
        """
        pass

    def trade(self):
        """
        模拟交易函数，根据信号和当前状态进行交易
        :return:
        """
        pass

    def log(self):
        """
        生成交易日志
        :return:
        """
        pass

    def summary(self):
        """
        生成统计报告
        :return:
        """
        pass

    def back_test(self):
        """
        基于历史数据进行回测
        :return:
        """
        pass

