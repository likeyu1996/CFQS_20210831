#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    Created by Klaus Lee on 2021/9/10
-------------------------------------------------
"""

import numpy as np
import pandas as pd

trading_log_dict = {'uid': 'Trading UID',
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
deposit_log_dict = {'uid': 'Deposit Change UID',
                         'tid': 'Trading UID',
                         'date': 'Deposit Change Date',
                         'direction': 'Deposit Change Direction',
                         'type': 'Deposit Change Type',
                         'amount': 'Deposit Change Amount',
                         }
trading_log = pd.DataFrame(columns=trading_log_dict.keys())
deposit_log = pd.DataFrame(columns=deposit_log_dict.keys())

print(trading_log)
print(deposit_log)
