from alive_progress import alive_bar
import numpy as np
import pandas as pd
import os
import threading

finalSymbols=[]
CANDLES_COUNT=100
POINTAPERCENT=70
POINTCPERCENT=30
crossMarginSymbolFile=open(os.getcwd()+"/crossMarginSymbols.txt","r")
crossMarginList=crossMarginSymbolFile.readlines()
crossMarginSymbolFile.close()

def checkForCnH(timeFrame,dataFile):
    try:
        DF =    pd.read_csv(os.getcwd()+'/data{}/{}'.format(timeFrame,dataFile))
        values  =   DF.to_numpy()
        noofcandles=len(values)
        validCupandHandle=False
        if noofcandles>=CANDLES_COUNT:
            #take last hundred candles
            #take first 30 candles find the high(mark it as A)
            ValueA= np.nanmax(values[noofcandles-CANDLES_COUNT:noofcandles-POINTAPERCENT,3])
            positionA=int(np.where(values[noofcandles-CANDLES_COUNT:noofcandles-POINTAPERCENT,3]==ValueA)[0][0])+noofcandles-CANDLES_COUNT
            # print(values[noofcandles-CANDLES_COUNT:noofcandles-POINTAPERCENT,3])
            # print(noofcandles)
            # print(positionA)
            # print(values[positionA,3])
            # check whether high is crossed with 1%fluctuation 
            # if not crossed check high from candle high to 70th candle
            if np.nanmax(values[positionA+1:,3])<=1.01*ValueA:
                # if second high is nearer to 1% fluctuation(mark it as C) 
                ValueC=np.nanmax(values[positionA+1:noofcandles-POINTCPERCENT,3])
                if ValueC>=0.99*ValueA:
                    positionC=int(np.where(values[positionA+1:noofcandles-POINTCPERCENT,3]==ValueC)[0][0])+positionA
                    # find the low between the postions A and C(mark it as B)
                    ValueB=np.nanmin(values[positionA:positionC,4])
                    # if difference between point A and B is min 3%
                    if ValueA/ValueB>=1.03:
                        # find the low from point C to end of the candles(mark it as point D)
                        # difference between the point C and D should be less than 50% of the difference from point C and B
                        # if all conditions are satisfied then it is a valid cup and handle
                        ValueD=np.nanmin(values[positionC:,4])
                        if ValueC-ValueD <= (ValueC-ValueB)/2:
                            validCupandHandle=True

        if(validCupandHandle):
            x=[]
            x.append(dataFile.split(".")[0]) #name
            x.append(values[len(values)-1,5])#currentPrice
            finalSymbols.append(x)
    except Exception as e:
        c=0

def checkForCupAndHandleAllTimeFrames():
    timeInterval=[5,15,30,60,120,240,480,1440]
    finalList=[]
    # totalCount=0
    # for interval in timeInterval:
    #     totalCount+=len(os.listdir(os.getcwd()+'/data{}'.format(interval)))
    for interval in timeInterval:
        # np.set_printoptions(precision=2)
        dataFiles   =   os.listdir(os.getcwd()+'/data{}'.format(interval))
        threadlist=[]
        for dataFile in dataFiles:
            t1=threading.Thread(target=checkForCnH,args=[interval,dataFile])
            t1.start()
            threadlist.append(t1)
        for th in threadlist:
            th.join()
        sorted_multi_list = sorted(finalSymbols, key=lambda x: float(x[1]),reverse=True)
        finalList.append(sorted_multi_list)
        finalSymbols.clear()
    return finalList