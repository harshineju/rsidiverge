from alive_progress import alive_bar
import numpy as np
import pandas as pd
import os
import threading

progressCount=0
finalSymbols=[]
crossMarginSymbolFile=open(os.getcwd()+"/crossMarginSymbols.txt","r")
crossMarginList=crossMarginSymbolFile.readlines()
crossMarginSymbolFile.close()

def checkDoubleBottom(timeFrame,dataFile):
    global finalSymbols
    localMinList=[]
    localMaxList=[]
    globalMinList=[]
    globalMaxList=[]
    # try:
    DF =    pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
    DF =    DF[-50:]
    np.set_printoptions(precision=2)
    values  =   DF.to_numpy()
    symbolName=dataFile.split(".")[0]
    
    #SPLIT 50 CANDLES INTO 8 CANDLE and 7PARTS OF 6 CANDLES
    localMinList.append(np.nanmin(values[0:8,5]))    
    localMaxList.append(np.nanmax(values[0:8,5]))

    for i in range(8,50,6):
        localMinList.append(np.nanmin(values[i:i+6,5]))    
        localMaxList.append(np.nanmax(values[i:i+6,5]))

    
    #FIND MAXIMUM OF LAST 20 CANDLES
    globalMinList.append(np.nanmin(values[30:50,5]))
    globalMaxList.append(np.nanmax(values[30:50,5]))

    #check for the last local bottom
    lastMinimum=localMinList[7]

    for i in range(7):
        if not lastMinimum<localMinList[i]:
            return
    
    if not (localMaxList[6]/lastMinimum)>1.01:
        return

    if not (localMinList[4]/lastMinimum>1.005 or localMinList[4]/lastMinimum<0.995):
        return

    if globalMaxList[0]==localMaxList[0]:
        x=[]
        x.append(symbolName)
        x.append(timeFrame)
        # x.append(symbolName+"\n" in crossMarginList)
        finalSymbols.append(x)
    # except Exception as e:
    #     print(e)
    #     print(dataFile,timeFrame)


def checkDoubleBottomAllTimeFrames():
    global progressCount,finalSymbols
    timeInterval=[5,15,30,60,120,240,480,1440,10080]
    totalCount=0
    for interval in timeInterval:
        totalCount+=len(os.listdir(os.getcwd()+'/data{}'.format(interval)))
    with alive_bar(totalCount) as bar:
        for interval in timeInterval:
            dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(interval))
            threadlist=[]
            for dataFile in dataFiles:
                t1=threading.Thread(target=checkDoubleBottom,args=[interval,dataFile])
                t1.start()
                threadlist.append(t1)
                bar()
            for th in threadlist:
                th.join()
    print(finalSymbols)

checkDoubleBottomAllTimeFrames()