from alive_progress import alive_bar
import numpy as np
import pandas as pd
import os
import talib
import threading

finalSymbols=[]
CANDLES_COUNT=20
crossMarginSymbolFile=open(os.getcwd()+"/crossMarginSymbols.txt","r")
crossMarginList=crossMarginSymbolFile.readlines()
crossMarginSymbolFile.close()

def checkForBuD(timeFrame,dataFile):
    try:
        DF =    pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
        values  =   DF.to_numpy()
        rsi = talib.RSI(values[:,5], timeperiod=14)
        lastRsi =   rsi[len(rsi)-1]
        if not len(rsi)<40:
            if lastRsi<=30:
                if timeFrame in [5,15,30,120,240]:
                    minRsi= np.nanmin(rsi[len(rsi)-20:len(rsi)-1])
                else:
                    minRsi= np.nanmin(rsi[len(rsi)-CANDLES_COUNT:len(rsi)-1])
                if lastRsi>minRsi:
                    symbolName=dataFile.split(".")[0]
                    position=int(np.where(rsi==minRsi)[0][0])
                    sellPrice=values[position,5]
                    currentPrice=values[len(values)-1,5]

                    if currentPrice<sellPrice:
                        # find the position where the price closed below the sell price
                        position2=1
                        for price in values[(position+1):,5]:
                            if price<sellPrice:
                                break
                            else:
                                position2+=1

                        # check whether it is a valid divergence(where the price didnt touch the price at rsi extreme)
                        validDivergence=True
                        for price in values[(position+position2+1):,3]: # 3 for high , 5 for close
                            if(price>=sellPrice):
                                validDivergence=False
                                break
                        if(validDivergence):
                            if float(sellPrice)/float(currentPrice) > 1.0:
                                x=[]
                                x.append(symbolName)
                                x.append("{:.2f}".format(((sellPrice/currentPrice)-1)*100))
                                x.append(sellPrice)
                                x.append(currentPrice)
                                x.append(symbolName+"\n" in crossMarginList)
                                finalSymbols.append(x)
    except Exception as e:
        print(e)
        print(dataFile,timeFrame)

def checkForBullishDivergence(timeFrame):
    np.set_printoptions(precision=2)
    dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(timeFrame))
    threadlist=[]
    for dataFile in dataFiles:
        t1=threading.Thread(target=checkForBuD,args=[timeFrame,dataFile])
        t1.start()
        threadlist.append(t1)
    for th in threadlist:
        th.join()  
    sorted_multi_list = sorted(finalSymbols, key=lambda x: float(x[1]),reverse=True)
    finalSymbols.clear()
    return sorted_multi_list

def checkForBullishDivergenceAllTimeFrames():
    global progressCount
    timeInterval=[5,15,30,60,120,240,480,1440,10080]
    finalList=[]
    totalCount=0
    for interval in timeInterval:
        totalCount+=len(os.listdir(os.getcwd()+'/data{}'.format(interval)))
    with alive_bar(totalCount,ctrl_c=True,title="Bullish Divergence ") as bar:
        for interval in timeInterval:
            np.set_printoptions(precision=2)
            dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(interval))
            threadlist=[]
            for dataFile in dataFiles:
                t1=threading.Thread(target=checkForBuD,args=[interval,dataFile])
                t1.start()
                threadlist.append(t1)
                bar()
            for th in threadlist:
                th.join()
            sorted_multi_list = sorted(finalSymbols, key=lambda x: float(x[1]),reverse=True)
            finalList.append(sorted_multi_list)
            finalSymbols.clear()
    return finalList

def checkForBearishDivergenceAllTimeFrames():
    global progressCount
    timeInterval=[5,15,30,60,120,240,480,1440,10080]
    finalList=[]
    totalCount=0
    for interval in timeInterval:
        totalCount+=len(os.listdir(os.getcwd()+'/data{}'.format(interval)))
    with alive_bar(totalCount,ctrl_c=True, title="Bearish Divergence ") as bar:
        for interval in timeInterval:
            np.set_printoptions(precision=2)
            dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(interval))
            threadlist=[]
            for dataFile in dataFiles:
                t1=threading.Thread(target=checkForBeD,args=[interval,dataFile])
                t1.start()
                threadlist.append(t1)
                bar()
            for th in threadlist:
                th.join()
            sorted_multi_list = sorted(finalSymbols, key=lambda x: float(x[1]),reverse=True)
            finalList.append(sorted_multi_list)
            finalSymbols.clear()
    return finalList

def checkForBeD(timeFrame,dataFile):
    try:
        DF =    pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
        values  =   DF.to_numpy()
        rsi = talib.RSI(values[:,5], timeperiod=14)
        lastRsi =   rsi[len(rsi)-1]
        if not len(rsi)<40:
            if lastRsi>=70:
                if timeFrame in [5,15,30,120,240]:
                    maxRsi= np.nanmax(rsi[len(rsi)-20:len(rsi)-1])
                else:
                    maxRsi= np.nanmax(rsi[len(rsi)-CANDLES_COUNT:len(rsi)-1])
                if lastRsi<maxRsi:
                    symbolName=dataFile.split(".")[0]
                    position=int(np.where(rsi==maxRsi)[0][0])
                    buyPrice=values[position,5]
                    currentPrice=values[len(values)-1,5]
                    if currentPrice>buyPrice:
                        # find the position where the price closed above the buy price
                        position2=1
                        for price in values[(position+1):,5]: # 4 for low and 5 for close
                            if price>buyPrice:
                                break
                            else:
                                position2+=1

                        # check whether it is a valid divergence(where the price didnt touch the price at rsi extreme)
                        validDivergence=True
                        for price in values[(position+position2+1):,4]:
                            if(price<=buyPrice):
                                validDivergence=False
                                break
                        if(validDivergence):
                            if float(currentPrice)/float(buyPrice) > 1.0:
                                x=[]
                                x.append(symbolName)
                                x.append("{:.2f}".format(((buyPrice/currentPrice)-1)*-100))
                                x.append(buyPrice)
                                x.append(currentPrice)
                                x.append(symbolName+"\n" in crossMarginList)
                                finalSymbols.append(x)
    except Exception as e:
        print(e)
        print(dataFile)
        print(timeFrame)
        return
    
def checkForBearishDivergence(timeFrame):
    np.set_printoptions(precision=2)
    dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(timeFrame))
    threadlist=[]
    for dataFile in dataFiles:
        t1=threading.Thread(target=checkForBeD,args=[timeFrame,dataFile])
        t1.start()
        threadlist.append(t1)
    for th in threadlist:
        th.join()
    sorted_multi_list = sorted(finalSymbols, key=lambda x: float(x[1]),reverse=True)
    finalSymbols.clear()
    return sorted_multi_list