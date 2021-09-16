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


# numpy完整print输出
np.set_printoptions(threshold=np.inf)
# pandas完整print输出
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)

ROOT_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(ROOT_PATH, 'Data')
RESULT_PATH = os.path.join(ROOT_PATH, 'Result')


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
        生成策略实例时要super(子类，self).__init__(参数1，参数2，....)

        """
        self.start_date = start_date
        self.end_date = end_date
        self.variety = variety
        self.freq = freq

        self.cash = cash

        self.signal = ''
        self.data = self.get_data()
        self.trans_cal, self.trade_dict = self.trade_calender()
        self.data_final = self.get_k()

        self.trading_log_dict = {'uid': 'Trading UID',
                                 'date': 'Trading Date',
                                 'name': 'Strategy Name',
                                 'variety': 'Future Varieties',
                                 'contract': 'Contract ID',
                                 'direction': 'Transaction Direction',
                                 'type': 'Transaction Type',
                                 'price': 'Transaction Price',
                                 'amount': 'Transaction Amount',
                                 'charge': 'Service Charge',
                                 }
        self.trading_log = pd.DataFrame(columns=self.trading_log_dict.keys())
        self.margin_log_dict = {'uid': 'Deposit Change UID',
                                'tid': 'Trading UID',
                                'date': 'Margin Change Date',
                                'direction': 'Margin Change Direction',
                                'type': 'Margin Change Type',
                                'amount': 'Margin Change Amount',
                                }
        self.margin_log = pd.DataFrame(columns=self.margin_log_dict.keys())
        self.position_dict = {'contract': 'Contract ID',
                              'direction': 'Position Direction',
                              'amount': 'Position Total Amount',
                              'cost': 'Position Average Cost',
                              'price': 'Position Price now',
                              }
        self.position = pd.DataFrame(columns=self.position_dict.keys())

    def get_data(self):
        """
        从数据库中选取策略所需的最小维度的数据
        开始日，结束日，策略品种，策略频率
        """
        print('Function {0} Must be Overridden'.format('get_data'))
        db = pd.read_csv(os.path.join(DATA_PATH, 'future.csv'))
        data = db.loc[db['contract'].str.contains(self.variety,
                                                  case=False, na=False, regex=False)]
        data['date'] = pd.to_datetime(data['date'])
        data.reset_index(inplace=True, drop=True)
        return data

    def trade_calender(self):
        """
        生成交易日历
        第二种方法得到的效果最优(类型一致)，但由于是单个修改不知道效率如何
        需要datetime则用data.loc[i, 'date'].to_pydatetime()
        法3生成的是numpy.datetime64，并非pandas下的timestamp，不可直接用于筛选
        """
        '''
        trade_cal = list(set(self.data.loc[:, 'date'].to_numpy(datetime.datetime)))
        trade_cal = [i.date() for i in trade_cal]
        trade_cal.sort()
        '''
        trade_cal = list(set(self.data.loc[i, 'date'] for i in range(len(self.data['date']))))
        trade_cal.sort()
        '''
        trans_cal = self.data.loc[:, 'date'].unique()
        trans_cal.sort()
        '''
        trade_dict = dict(zip(trade_cal, [i + 1 for i in range(len(trade_cal))]))
        return trade_cal, trade_dict

    def get_k(self):
        """
        绘制可交易合约K线表和图
        # 以实际交易日序数和交易日期生成交易字典，以此计算实际交易日间隔而非通过日期
        # 数据处理方案：先筛选品种，再(根据交易所移仓规则+交易主力合约规则)筛选可交易合约
        # 交易所和期货公司移仓规则触发移仓时，发出平仓和开仓新合约的信号
        # 以最大持仓量为标准选择主力合约，主力合约一般来说交易量最大，一般来说一个主力合约会连续存在一段时间
        # 当主力合约交易量非最大以及主力合约发生变动时，记入日志
        # 可交易合约不会进入交割月，因此进入交割月的主力合约不会被认为是可交易合约
        # 或者说，可交易合约发生变化时，自动发出平仓和重新开仓的信号，平主力合约，开次主力合约
        """
        trade_cal = self.trans_cal

        # TODO：策略系统成型后再加入保证金系统（因为保证金是会根据交割月和涨跌停板而变动的）
        # 交易日循环->选取当日主力合约和次主力合约->检验主力合约是否进入交割月(同年同月)->是，次主力；否，主力
        k_dict = {'date': 'Trading Date',
                  'contract': 'Contract chosen',
                  'preclose': 'pre close',
                  'presettle': 'pre settle',
                  'open': 'open',
                  'high': 'high',
                  'low': 'low',
                  'close': 'close',
                  'settle': 'settle',
                  'ch1': 'close - pre settle',
                  'ch2': 'settle - pre settle',
                  'volume': 'volume',
                  'amount': 'volume * average price',
                  'oi': 'open interest',
                  }
        k_append_dict = {'contract_oi': 'Contract with most OI',
                         'contract_vol': 'Contract with most volume',
                         }
        k_df = pd.DataFrame(columns=k_dict.keys())
        k_append_df = pd.DataFrame(columns=k_append_dict.keys())
        for i in trade_cal:
            data_today = self.data.loc[self.data['date'] == i]
            today_oi = data_today.sort_values(by=['oi', 'volume'], ascending=False, inplace=False)\
                .reset_index(inplace=False, drop=True)
            today_volume = data_today.sort_values(by=['volume', 'oi'], ascending=False, inplace=False)\
                .reset_index(inplace=False, drop=True)
            if today_oi.loc[0, 'contract'] != today_volume.loc[0, 'contract']:
                # TODO:记入日志
                print('{0}：交易量最大合约为{2}，而非主力合约{1}'
                      .format(i.to_pydatetime().date(), today_oi.loc[0, 'contract'], today_volume.loc[0, 'contract']))
            contract_oi = today_oi.loc[0, 'contract']
            contract_vol = today_volume.loc[0, 'contract']
            today_date = i.to_pydatetime()
            today_yy = str(today_date.year)[-2:]
            today_mm = str(today_date.month) if len(str(today_date.month)) == 2 else '0'+str(today_date.month)
            contract_oi_yy = contract_oi[-4:-2]
            contract_oi_mm = contract_oi[-2:]
            # 获得合约年月和当前年月，并比较判断当前是否为主力交割月，默认合约代码格式为VVYYMM
            if today_yy == contract_oi_yy and today_mm == contract_oi_mm:
                # 主力合约进入交割月，主力合约不可交易
                k_df = k_df.append(today_volume.iloc[0, :], ignore_index=True)
            else:
                k_df = k_df.append(today_oi.iloc[0, :], ignore_index=True)
            k_append_df = k_append_df.append({'contract_oi': contract_oi, 'contract_vol': contract_vol}, ignore_index=True)
        k_final = pd.concat([k_df, k_append_df], axis=1)
        print(k_final.loc[:, 'contract'].to_numpy())
        k_final.to_csv(os.path.join(RESULT_PATH, 'data_clean.csv'), index=False)
        return k_final

    def signal(self, date):
        """
        构建策略，生成做多做空信号
        计算盈亏的时候并非通过保证金，而是通过价格单数
        """
        # 计算指标并
        # print('Function {0} Must be Overridden'.format('signal'))

    def update_status(self):
        """
        当前各种状态（每次交易和收盘后都更新）
        :return:
        """
        pass

    def trade(self):
        """
        模拟交易，根据信号和当前状态进行交易
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
        逐日循环回测，只在开盘和收盘时交易
        """
        for date in self.trans_cal:
            self.signal(date)
        pass


a = Strategy(start_date=datetime.datetime, end_date=datetime.datetime, variety='rb')

