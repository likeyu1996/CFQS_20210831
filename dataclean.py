#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    Created by Klaus Lee on 2021/9/8
-------------------------------------------------
"""

import numpy as np
import pandas as pd
import datetime
import os

ROOT_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(ROOT_PATH, 'DB')
TEMP_PATH = os.path.join(DB_PATH, 'csv')
DATA_PATH = os.path.join(ROOT_PATH, 'Data')


def get_filename(path, filetype, accurate=False):
    name = []
    for root, dirs, files in os.walk(path):
        for i in files:
            if accurate is False:
                if os.path.splitext(i)[1].lower() == filetype.lower():
                    name.append(i)
            else:
                if os.path.splitext(i)[1] == filetype:
                    name.append(i)
    return name


def filter_fu_op(file_list):
    for csv_file in file_list:
        print(csv_file)
        # 日期格式化
        data = pd.read_csv(os.path.join(TEMP_PATH, csv_file), skiprows=[1, 2], na_values=np.nan)
        data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
        # 填充合约代码
        contract_new = data.loc[:, 'contract'].fillna(method='pad')
        data['contract'] = contract_new
        # 分离期货和期权数据
        data_future = data.loc[data['contract'].str.len() <= 6]\
            .sort_values(by=['contract', 'date'], ascending=True, inplace=False)\
            .reset_index(inplace=False, drop=True)
        data_option = data.loc[data['contract'].str.len() > 6]\
            .sort_values(by=['contract', 'date'], ascending=True, inplace=False)\
            .reset_index(inplace=False, drop=True)
        data_future.to_csv(os.path.join(DB_PATH, 'future'+csv_file), index=False)
        data_option.to_csv(os.path.join(DB_PATH, 'option'+csv_file), index=False)


def merge_fu_op(file_list, dev_type):
    # 将分离的数据合并
    if dev_type in ['fu', 'future']:
        dev_type = 'future'
    elif dev_type in ['op' or 'option']:
        dev_type = 'option'
    else:
        print('ERROR: Unknown dev_type {0}'.format(dev_type))
        return
    file_list_new = [dev_type + i for i in file_list]
    db_list = [pd.read_csv(os.path.join(DB_PATH, i)) for i in file_list_new]
    db_new = pd.concat(db_list)
    db_new.sort_values(by=['contract', 'date'], ascending=True, inplace=True)
    db_new.reset_index(inplace=True, drop=True)
    db_new.to_csv(os.path.join(DATA_PATH, dev_type+'.CSV'), index=False)
    print('Complete: {0}.CSV has {1} rows'.format(dev_type, len(db_new.index)))


csv_list = get_filename(TEMP_PATH, '.csv', accurate=False)
# filter_fu_op(csv_list)
merge_fu_op(csv_list, 'fu')
merge_fu_op(csv_list, 'op')



