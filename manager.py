from binance import Client
import talib
import pandas as pd
import constants

import numpy as np
from candle_rankings import candle_rankings
import talib
from itertools import compress



class BinanceManager:

    bin_key = constants.BINANCE_KEY
    bin_secret = constants.BINANCE_SECRET
    client =""
    binance_raw_data = []
    #binance_future_pairs = []

    def getData(self,pair=constants.COIN_PAIR):
        self.client = Client(api_key=self.bin_key, api_secret= self.bin_secret)
        #datas = self.client.get_historical_klines(pair, constants.TIME_INTERVAL, "1 Jan, 2023")
        datas = self.client.futures_historical_klines(pair, constants.TIME_INTERVAL,"1 Jan 2023")
        my_df = pd.DataFrame(datas)
        my_df.columns  = ['open_time','open','high','low','close','volume','close_time','qav','num_trades','taker_base_trade_volume','taker_quote_vol','ignore']
        #my_df = my_df.iloc[:,0:6]
         # time column is converted to "YYYY-mm-dd hh:mm:ss" ("%Y-%m-%d %H:%M:%S")
        posix_time = pd.to_datetime(my_df['open_time']/1000.0, unit='s')
        # append posix_time
        my_df.insert(0, "date", posix_time)
        my_df.insert(1,"name", pair)
        # drop unix time stamp
        my_df.drop("open_time", axis = 1, inplace = True)
        self.binance_raw_data = my_df.iloc[:,0:6] 

    def getFutureAllPairs(self):
        #BURASI KULLANILMIYOR ŞU ANDA......
        temp = self.client.futures_coin_ticker()
        for x in temp:
            self.binance_future_pairs.append(x['pair'])
    


class CandlestickRecognizer:
    open =[]
    high =[]
    low =[]
    close =[]

    
    def recognize_candlestick(self,df):
        """
        Recognizes candlestick patterns and appends 2 additional columns to df;
        1st - Best Performance candlestick pattern matched by www.thepatternsite.com
        2nd - # of matched patterns
        """

        self.open = df['open'].astype(float)
        self.high = df['high'].astype(float)
        self.low = df['low'].astype(float)
        self.close = df['close'].astype(float)

        candle_names = talib.get_function_groups()['Pattern Recognition']
        
        # patterns not found in the patternsite.com
        exclude_items = ('CDLCOUNTERATTACK',
                        'CDLLONGLINE',
                        'CDLSHORTLINE',
                        'CDLSTALLEDPATTERN',
                        'CDLKICKINGBYLENGTH')

        candle_names = [candle for candle in candle_names if candle not in exclude_items]
        
        try:
            # create columns for each candle
            for candle in candle_names:
                # below is same as;
                # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
                df[candle] = getattr(talib, candle)(self.open, self.high, self.low, self.close)


            df['candlestick_pattern'] = np.nan
            df['candlestick_match_count'] = np.nan
            for index, row in df.iterrows():

                # no pattern found
                if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
                    df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
                    df.loc[index, 'candlestick_match_count'] = 0
                # single pattern found
                elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
                    # bull pattern 100 or 200
                    if any(row[candle_names].values > 0):
                        pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                        df.loc[index, 'candlestick_pattern'] = pattern
                        df.loc[index, 'candlestick_match_count'] = 1
                    # bear pattern -100 or -200
                    else:
                        pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                        df.loc[index, 'candlestick_pattern'] = pattern
                        df.loc[index, 'candlestick_match_count'] = 1
                # multiple patterns matched -- select best performance
                else:
                    # filter out pattern names from bool list of values
                    patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
                    container = []
                    for pattern in patterns:
                        if row[pattern] > 0:
                            container.append(pattern + '_Bull')
                        else:
                            container.append(pattern + '_Bear')
                    rank_list = [candle_rankings[p] for p in container]
                    if len(rank_list) == len(container):
                        rank_index_best = rank_list.index(min(rank_list))
                        df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                        df.loc[index, 'candlestick_match_count'] = len(container)
            # clean up candle columns
            cols_to_drop = candle_names + list(exclude_items)
            df.drop(cols_to_drop, axis = 1, inplace = True)
        except:
            pass

        return df




