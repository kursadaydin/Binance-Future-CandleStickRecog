from manager import BinanceManager
from manager import CandlestickRecognizer
import constants

my_binance = BinanceManager()
my_cst_recog = CandlestickRecognizer()
temp = []
text = "Parite:{} Sonuç:{}"

for i in constants.COIN_PAIRS:
    my_binance.getData(pair=i) 
    my_new_df = my_cst_recog.recognize_candlestick(df=my_binance.binance_raw_data)
    temp_name =(my_new_df[-1:]['name']).values[0]
    temp_result =(my_new_df[-1:]['candlestick_pattern']).values[0]
    print(text.format(temp_name,temp_result))
    if temp_result != "NO_PATTERN":
        my_cst_recog.getVisulation(my_binance.binance_raw_data)

    



