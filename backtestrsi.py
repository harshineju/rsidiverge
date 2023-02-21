from binance.client import Client
from binance.enums import *
import pandas as pd
import numpy as np
import os
import talib
import config
import time
import numpy as np
import datetime
from main1 import createSymbolFile

symbol='JASMYUSDT'
TIME=120
TIMEPERIOD=14
endTime=int(time.time())*1000
RSI_MIN_VALUE=30
RSI_MAX_VALUE=70
TIMEPERIODTOCHECK=20
timedurationlist=[]
maxRsiList=[]

def getIntervalArguement(value):
    switcher = {
        5: Client.KLINE_INTERVAL_5MINUTE,
        15: Client.KLINE_INTERVAL_15MINUTE,
        30: Client.KLINE_INTERVAL_30MINUTE,
        60: Client.KLINE_INTERVAL_1HOUR,
        120: Client.KLINE_INTERVAL_2HOUR,
        240: Client.KLINE_INTERVAL_4HOUR,
        480: Client.KLINE_INTERVAL_8HOUR,
        1440: Client.KLINE_INTERVAL_1DAY,
        10080: Client.KLINE_INTERVAL_1WEEK
    }    
    return switcher.get(value, "nothing")

def isValidSymbol(symbolName):
    symbolList=createSymbolFile('dummy')
    symbolName+='\n'
    if symbolName in symbolList:
        return True
    else:
        return False

def collectData():
    global symbol,TIME
    symbol=input("Enter coin pair:")
    symbol=symbol.upper()
    while not isValidSymbol(symbol):
        symbol=input("Enter correct symbol pair:")
        symbol=symbol.upper()
    TIME=int(input("Enter candle duration in minutes:"))
    timelist=[5,15,30,60,120,240,480,1440,10080]
    while not TIME in timelist:
        TIME=int(input("Enter candle duration in minutes:"))
    print("Collecting Data")
    while True:
        try:
            client = Client(config.API_KEY, config.API_SECRET)
            # print(client.get_margin_symbol(symbol=symbol))
            startTime=int(client._get_earliest_valid_timestamp(symbol,getIntervalArguement(TIME)))
            if TIME==5 and endTime-startTime>12614400:
                startTime=int(time.time()-12614400)*1000
            print(startTime)
            print(endTime)
            klines = client.get_historical_klines(symbol, getIntervalArguement(TIME),startTime,endTime)
            # print(sys.getsizeof(klines))
            break
        except Exception as e:
            print(e)
            time.sleep(100)

    #write kline to file

    a  = np.asarray(klines)
    try:
        DF = pd.DataFrame(np.delete(a,(6,7,8,9,10,11),1))
    except:
        print("ERROR")
    os.makedirs(os.getcwd()+"/backtest", exist_ok=True)
    symDataFile = open(os.getcwd()+"/backtest/"+symbol+".csv","w")
    DF.to_csv(symDataFile)
    symDataFile.close()

def bearishDivergenceBacktest(values,rsiValues):
    count=-1
    validDivergenceCount=0
    divergenceSortedCount=0
    #for bearish divergence
    for rsi in rsiValues:
        count+=1
        if count<34:
            continue
        if not np.isnan(rsi):
            if rsi>=RSI_MAX_VALUE:
                previousRsiValues=rsiValues[count-TIMEPERIODTOCHECK:count]
                maxRsi= np.nanmax(previousRsiValues)
                if maxRsi in maxRsiList:
                    continue
                if rsi<maxRsi:
                    position=int(np.where(previousRsiValues==maxRsi)[0][0])
                    buyPricePosition=count-TIMEPERIODTOCHECK+position
                    buyPrice=values[buyPricePosition,5] #rsi extreme price
                    validDivergence=False
                    currentPrice=values[count,5]
                    if currentPrice>buyPrice:
                        # find the position where the price closed above the buy price
                        position2=1
                        for price in values[(buyPricePosition+1):count,5]:
                            if price>buyPrice:
                                break
                            else:
                                position2+=1
                        
                        # check whether it is a valid divergence(where the price didnt touch the price at rsi extreme)
                        for price in values[(buyPricePosition+position2):count,5]:
                            if(price<=buyPrice):
                                validDivergence=False
                                break
                            else:
                                validDivergence=True
                        if validDivergence:
                            #check whether divergence is sorted
                            maxRsiList.append(maxRsi)
                            validDivergenceCount+=1
                            timedurationtosort=1
                            divergenceSorted=False
                            for price in values[(count):,4]:
                                if price<=buyPrice:
                                    divergenceSortedCount+=1
                                    divergenceSorted=True
                                    break
                                else:
                                    timedurationtosort+=1
                            if(divergenceSorted):
                                timedurationlist.append(timedurationtosort)
                            else:
                                print(datetime.datetime.fromtimestamp(int(values[count,1])/1000))
    print("Divergence Formed=",validDivergenceCount)
    print("Divergence Sorted=",divergenceSortedCount)

def bullishDivergenceBacktest(values,rsiValues):
    #for bullish divergence
    count=-1
    validDivergenceCount=0
    divergenceSortedCount=0
    minRsiList=[]
    for rsi in rsiValues:
        count+=1
        if count<34:
            continue
        if not np.isnan(rsi):
            if rsi<=RSI_MIN_VALUE:
                previousRsiValues=rsiValues[count-TIMEPERIODTOCHECK:count]
                minRsi= np.nanmin(previousRsiValues)
                if minRsi in minRsiList:
                   continue
                if rsi>minRsi:
                    position=int(np.where(previousRsiValues==minRsi)[0][0])
                    sellPricePosition=count-TIMEPERIODTOCHECK+position
                    sellPrice=values[sellPricePosition,5] #rsi extreme price
                    validDivergence=False
                    position2=1
                    currentPrice=values[count,5]
                    if currentPrice<sellPrice:
                        # find the position where the price closed below the sell price
                        for price in values[(sellPricePosition+1):count,5]:
                            if price<sellPrice:
                                break
                            else:
                                position2+=1
                        # print(datetime.datetime.fromtimestamp(int(values[sellPricePosition,1])/1000))
                        # print(sellPrice)
                        # check whether it is a valid divergence(where the price didnt touch the price at rsi extreme)
                        for price in values[(sellPricePosition+position2+1):count,5]:
                            if(price>=sellPrice):
                                validDivergence=False
                                break
                            else:
                                validDivergence=True
                        if validDivergence:
                            #check whether divergence is sorted
                            minRsiList.append(minRsi)
                            validDivergenceCount+=1
                            timedurationtosort=1
                            divergenceSorted=False
                            for price in values[(count):,3]:
                                if price>=sellPrice:
                                    divergenceSortedCount+=1
                                    divergenceSorted=True
                                    break
                                else:
                                    timedurationtosort+=1
                            if(divergenceSorted):
                                timedurationlist.append(timedurationtosort)                                
                            else:
                                print(datetime.datetime.fromtimestamp(int(values[sellPricePosition,1])/1000))
    print(timedurationlist)                        
    print("Divergence Formed=",validDivergenceCount)
    print("Divergence Sorted=",divergenceSortedCount)

try:
    collectData()
    DF =    pd.read_csv(os.getcwd()+'/backtest/'+symbol+'.csv')
    values  =   DF.to_numpy()
    rsiValues = talib.RSI(values[:,5], timeperiod=TIMEPERIOD)
    while(True):
        print("1.bullish divergence\n2.bearish divergence\n3.collectDataForNewPair\n4.Exit")
        choice=input("Enter choice:")
        if choice=='1':
            bullishDivergenceBacktest(values,rsiValues)
        elif choice=='2':
            bearishDivergenceBacktest(values,rsiValues)
        elif choice=='3':
            collectData()
            DF =    pd.read_csv(os.getcwd()+'/backtest/'+symbol+'.csv')
            values  =   DF.to_numpy()
            rsiValues = talib.RSI(values[:,5], timeperiod=TIMEPERIOD)
        elif choice=='4':
            break
        timedurationlist=[]
except Exception as e:
    print(e)