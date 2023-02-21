import time
from alive_progress import alive_bar
from collectHistoricalData import showProgressBar
from dataHandler import checkForBearishDivergenceAllTimeFrames, checkForBullishDivergenceAllTimeFrames
from cupandhandle import checkForCupAndHandleAllTimeFrames
from collectHistoricalData import createData,updateDataForFiveMinutes,updateDataForTwoHours
from collectHistoricalData import collectDataFor5mins,collectDataForTwoHour
from collectHistoricalData import collectWeeklyData, updateWeeklyData
import os
import threading
from datetime import datetime
import pickle
import pandas as pd
import numpy as np

def createSymbolFile(client):
    allSymbols=[]
    if(not os.path.isfile(os.getcwd()+"/allSymbols.txt")):
        tickers = (client.get_all_tickers())
        symbolFile = open(os.getcwd()+"/allSymbols.txt","w")
        for sym in tickers:
            if(sym['symbol'][-4:]=="USDT"):
                allSymbols.append(sym['symbol']+"\n")
        symbolFile.writelines(allSymbols)
        symbolFile.close()
    else:
        symbolFile = open(os.getcwd()+"/allSymbols.txt","r")
        allSymbols = symbolFile.readlines()
        symbolFile.close()
    # marginPairs=client.get_margin_all_pairs()
    # crossMarginSymbolFile=open(os.getcwd()+"/crossMarginSymbols.txt","w")
    # for symbol in marginPairs:
    #     if symbol['quote']=='USDT':
    #         crossMarginSymbolFile.write(symbol['symbol']+"\n")
    # crossMarginSymbolFile.close()
    return allSymbols
    
def collectData(allSymbols,timeFrame,client):
    threadlist=[]
    for symbol in allSymbols:
        t1=threading.Thread(target=createData,args=[symbol,timeFrame,client])
        t1.start()
        threadlist.append(t1)
        requestCount =  int(client.response.headers['x-mbx-used-weight-1m'])
        while(requestCount+threading.active_count()*2>1150):
            if requestCount>1190:
                time.sleep(5)
                client.ping()
            else:
                time.sleep(1)
                client.ping()
            requestCount=int(client.response.headers['x-mbx-used-weight-1m'])
    for th in threadlist:
        th.join()
    return True

def collectData1(client):
    allSymbols=createSymbolFile(client)
    executed=False
    if not os.path.isfile(os.getcwd()+"/data5/BTCUSDT.csv"):
        collectDataFor5mins(allSymbols,client)
        executed=True
    if not os.path.isfile(os.getcwd()+"/data120/BTCUSDT.csv"):
        collectDataForTwoHour(allSymbols,client)
    if not os.path.isfile(os.getcwd()+"/data10080/BTCUSDT.csv"):
        collectWeeklyData(allSymbols,client)
    if(executed):
        writeDivergenceResultToFile()
        time.sleep(900)
    fiveMinuteDataCollected=False
    twoHourDataCollected=False
    fileLocation=os.getcwd()+"/data5/BTCUSDT.csv"
    DF=pd.read_csv(fileLocation,dtype={"0":(np.unicode_),"1":str,"2":str,"3":str,"4":str,"5":str})
    lastTime=int(int(DF.iloc[-1][1])/1000)
    print("5mindiff:"+str(int(time.time()-lastTime)))
    if int(time.time())-lastTime>150000:
        collectDataFor5mins(allSymbols,client)
        fiveMinuteDataCollected=True
    fileLocation=os.getcwd()+"/data120/BTCUSDT.csv"
    DF=pd.read_csv(fileLocation,dtype={"0":(np.unicode_),"1":str,"2":str,"3":str,"4":str,"5":str})
    lastTime=int(int(DF.iloc[-1][1])/1000)
    print("2hrdiff:"+str(int(time.time()-lastTime)))
    if int(time.time())-lastTime>3600000:
        collectDataForTwoHour(allSymbols,client)
        twoHourDataCollected=True
    print("updating Data")
    totalCount=0
    if not fiveMinuteDataCollected:
        t1=threading.Thread(target=updateDataForFiveMinutes,args=[client])
        t1.start()
        totalCount=len(os.listdir(os.getcwd()+"/data5"))*2
    if not twoHourDataCollected:
        t2=threading.Thread(target=updateDataForTwoHours,args=[client])
        t2.start()
        totalCount+=len(os.listdir(os.getcwd()+"/data120"))*2
        t3=threading.Thread(target=updateWeeklyData,args=[client])
        t3.start()
        totalCount+=len(os.listdir(os.getcwd()+"/data10080"))
    t4=threading.Thread(target=showProgressBar,args=[totalCount])
    t4.start()
    t4.join()
    week=0
    while(True):
        writeDivergenceResultToFile()
        seconds=0
        with alive_bar(900,ctrl_c=True,title="Time Remaining") as bar:
            while(seconds<900):
                seconds+=1
                bar()
                time.sleep(1)
        totalCount=len(os.listdir(os.getcwd()+"/data5"))*2
        t1=threading.Thread(target=updateDataForFiveMinutes,args=[client])
        t1.start()
        t2=threading.Thread(target=updateDataForTwoHours,args=[client])
        t2.start()
        week+=1
        totalCount+=len(os.listdir(os.getcwd()+"/data120"))*2
        if week==95:
            t3=threading.Thread(target=updateWeeklyData,args=[client])
            t3.start()
            week=0
            totalCount+=len(os.listdir(os.getcwd()+"/data10080"))
        t4=threading.Thread(target=showProgressBar,args=[totalCount])
        t4.start()
        t4.join()

def getLastModified():
    lastTime=[]
    timeInterval=[5,15,30,60,120,240,480,1440,10080]
    for t in timeInterval:
        if os.path.isfile(os.getcwd()+f"/data{t}/BTCUSDT.csv"):
            lastTime.append(datetime.fromtimestamp(round(os.path.getmtime(os.getcwd()+f"/data{t}/BTCUSDT.csv"))))
        else:
            lastTime.append("No data")
    if os.path.isfile(os.getcwd()+"/divergenceResults/bullish.csv"):
        lastTime.append(datetime.fromtimestamp(round(os.path.getmtime(os.getcwd()+"/divergenceResults/bullish.csv"))))
        lastTime.append(datetime.fromtimestamp(round(os.path.getmtime(os.getcwd()+"/divergenceResults/bearish.csv"))))    
    return lastTime

def checkDivergence(divergenceType):
    if divergenceType=='bullish':
        result=checkForBullishDivergenceAllTimeFrames()
    else:
        result=checkForBearishDivergenceAllTimeFrames()
    return result

def checkCupAndHandle():
    result=checkForCupAndHandleAllTimeFrames()
    return result


def writeDivergenceResultToFile():
    result=checkDivergence('bullish')
    os.makedirs(os.getcwd()+"/divergenceResults", exist_ok=True)
    file = open(os.getcwd()+"/divergenceResults/bullish.csv","wb")
    pickle.dump(result,file)
    file.close()
    result=checkDivergence('bearish')
    file = open(os.getcwd()+"/divergenceResults/bearish.csv","wb")
    pickle.dump(result,file)
    file.close()
    print("Finished")