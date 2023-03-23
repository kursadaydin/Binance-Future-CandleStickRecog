from manager import BinanceManager
from manager import CandlestickRecognizer
import constants

my_binance = BinanceManager()
my_cst_recog = CandlestickRecognizer()
temp = []

for i in constants.COIN_PAIRS:
    my_binance.getData(pair=i) 
    my_new_df = my_cst_recog.recognize_candlestick(df=my_binance.binance_raw_data)
    temp.append(my_new_df.iloc[-1:])
print(temp)


