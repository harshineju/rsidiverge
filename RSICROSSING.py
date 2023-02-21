import os
import threading
import talib
import pandas as pd
import numpy as np

RSI_CROSSING_VALUE_DOWN =    30
RSI_CROSSING_VALUE_UP   =   70

finalList   =   []

def checkRsiCrossedUp(timeFrame, rsiValue=RSI_CROSSING_VALUE_DOWN):
    global finalList
    dataFiles=  os.listdir(os.getcwd()+"/data"+str(timeFrame))
    finalSymbols=[]
    print(rsiValue)
    for dataFile in dataFiles:
        DF      =   pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
        values  =   DF.to_numpy()
        rsi     =   talib.RSI(values[:,5], timeperiod=14)
        if pd.isna(rsi[len(rsi)-1]):
            continue
        lastRsi =   int(rsi[len(rsi)-1])
        if not len(rsi)<40:
            minRsi= int(np.nanmin(rsi[len(rsi)-20:len(rsi)-1]))
            if lastRsi<=int(rsiValue)+10 and lastRsi>=int(rsiValue) and minRsi<int(rsiValue):
                symbolName=dataFile.split(".")[0]
                currentPrice=values[len(values)-1,5]
                x=[]
                x.append(symbolName)
                x.append("{:.2f}".format((currentPrice)))
                finalSymbols.append(x)
    finalList.append(finalSymbols)

def checkRsiCrossedDown(timeFrame, rsiValue=RSI_CROSSING_VALUE_UP):
    dataFiles=  os.listdir(os.getcwd()+"/data"+str(timeFrame))
    global finalList
    finalSymbols=[]
    for dataFile in dataFiles:
        DF      =   pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
        values  =   DF.to_numpy()
        rsi = talib.RSI(values[:,5], timeperiod=14)
        if pd.isna(rsi[len(rsi)-1]):
            continue
        lastRsi =   int(rsi[len(rsi)-1])
        rsiValue=int(rsiValue)
        if not len(rsi)<40:
            maxRsi= int(np.nanmax(rsi[len(rsi)-20:len(rsi)-1]))
            if lastRsi>=rsiValue-10 and lastRsi<=rsiValue and maxRsi>rsiValue:
                symbolName=dataFile.split(".")[0]
                currentPrice=values[len(values)-1,5]
                x=[]
                x.append(symbolName)
                x.append("{:.2f}".format((currentPrice)))
                finalSymbols.append(x)
    finalList.append(finalSymbols)

def checkRsiCrossed(divergenceType,rsiValue):
    global finalList
    finalList=[]
    timeInterval=[5,15,30,60,120,240,480,1440,10080]
    threadList=[]
    if(divergenceType=="bullish"):
        for interval in timeInterval:
            if rsiValue=="" or rsiValue==None:
                rsiValue=RSI_CROSSING_VALUE_DOWN
            t1=threading.Thread(target=checkRsiCrossedUp,args=[interval,rsiValue])
            t1.start()
            threadList.append(t1)
    else:
        for interval in timeInterval:
            if rsiValue=="" or rsiValue==None:
                rsiValue=RSI_CROSSING_VALUE_UP
            t1=threading.Thread(target=checkRsiCrossedDown,args=[interval,rsiValue])
            t1.start()
            threadList.append(t1)
    for th in threadList:
        th.join()
    return finalList