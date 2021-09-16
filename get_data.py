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

ROOT_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(ROOT_PATH, 'Data')
RESULT_PATH = os.path.join(ROOT_PATH, 'Result')

# df = pro.index_daily(ts_code='CU.NH', start_date='20180101', end_date='20210901')



