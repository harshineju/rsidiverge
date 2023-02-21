import os
import threading
import time
import urllib.request
from datetime import datetime
import numpy as np
import pandas as pd
from alive_progress import alive_bar
from binance.client import Client


progresscount=0

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

def internet_on():
    try:
        urllib.request.urlopen('http://google.com', timeout=2)
        return True
    except:
        return False

def createData(symbol,timeFrame, connectionClient):
    timeFrame   =   int(timeFrame)
    sym = symbol
    sym = sym[0:len(sym)-1]
    startTime   =   (int(time.mktime( datetime.now().timetuple()))-(50*60*timeFrame))*1000 #before 50 candles time
    endTime =   int(time.mktime(datetime.now().timetuple()))*1000
    while True:
        try:
            klines = connectionClient.get_historical_klines(sym, getIntervalArguement(timeFrame),startTime,endTime)
            break
        except:
            print("Retying after 10 seconds")
            time.sleep(10)
    a  = np.asarray(klines)
    try:
        DF = pd.DataFrame(np.delete(a,(6,7,8,9,10,11),1))
    except:
        return None
    os.makedirs(os.getcwd()+"/data"+str(timeFrame), exist_ok=True)
    symDataFile = open(os.getcwd()+"/data"+str(timeFrame)+"/"+sym+".csv","w")
    DF.to_csv(symDataFile)
    symDataFile.close()

def collectDataFor5mins(allSymbols,connectionClient):
    for symbol in allSymbols:
        t1=threading.Thread(target=createDataFor5minutes,args=[symbol,connectionClient])
        requestCount =  int(connectionClient.response.headers['x-mbx-used-weight-1m'])
        print(symbol,requestCount)
        while(requestCount+threading.active_count()*4>1100):
                if requestCount>1190:
                    time.sleep(5)
                    connectionClient.ping()
                else:
                    time.sleep(1)
                    connectionClient.ping()
                requestCount=int(connectionClient.response.headers['x-mbx-used-weight-1m'])
                print(symbol,requestCount)
        t1.start()
    createDataForOtherTimeFrames()

def collectDataForTwoHour(allSymbols,connectionClient):
    for symbol in allSymbols:
        t1=threading.Thread(target=createDataForTwoHours,args=[symbol,connectionClient])
        requestCount =  int(connectionClient.response.headers['x-mbx-used-weight-1m'])
        while(requestCount+threading.active_count()*4>1100):
                if requestCount>1190:
                    time.sleep(5)
                    connectionClient.ping()
                else:
                    time.sleep(1)
                    connectionClient.ping()
                requestCount=int(connectionClient.response.headers['x-mbx-used-weight-1m'])
                print(symbol,requestCount)
        print(symbol,requestCount)
        t1.start()
    createDataForOtherHigherTimeFrames()

def createDataFor5minutes(symbol,connectionClient):
    sym = symbol
    sym = sym[0:len(sym)-1]
    startTime=int(time.time())-round(time.time())%3600-50*3600
    while True:
        try:
            klines = connectionClient.get_historical_klines(sym, Client.KLINE_INTERVAL_5MINUTE, startTime*1000,int(time.time()*1000))
            break
        except:
            print("Retying after 10 seconds")
            time.sleep(10)
    a=np.asarray(klines)
    try:
        DF = pd.DataFrame(np.delete(a,(6,7,8,9,10,11),1))
    except:
        return None
    os.makedirs(os.getcwd()+"/data5", exist_ok=True)
    symDataFile = open(os.getcwd()+"/data5/"+sym+".csv","w")
    DF.to_csv(symDataFile)
    symDataFile.close()

def createDataForTwoHours(symbol,connectionClient):
    sym = symbol
    sym = sym[0:len(sym)-1]
    startTime=int(time.time())-round(time.time())%86400-50*24*3600
    while True:
        try:
            klines = connectionClient.get_historical_klines(sym, Client.KLINE_INTERVAL_2HOUR, startTime*1000,int(time.time()*1000))
            break
        except:
            print("Retying after 10 seconds")
            time.sleep(10)
    a=np.asarray(klines)
    try:
        DF = pd.DataFrame(np.delete(a,(6,7,8,9,10,11),1))
    except:
        return None
    os.makedirs(os.getcwd()+"/data120", exist_ok=True)
    symDataFile = open(os.getcwd()+"/data120/"+sym+".csv","w")
    DF.to_csv(symDataFile)
    symDataFile.close()

def createDataForOtherTimeFrames():
    global progresscount
    dataFiles=os.listdir(os.getcwd()+'/data5')
    for datafile in dataFiles:
        DF =    pd.read_csv(os.getcwd()+'/data5/{}'.format(datafile))
        values  =   DF.to_numpy()
        i=0
        a=0
        b=0

        fifminutelist=[]
        thirminutelist=[]
        onehourlist=[]
        while i+2<len(values):
            fifminutelist.append(getTempList(values,i,3))
            i+=3
            
            if a+5<len(values):
                thirminutelist.append(getTempList(values,a,6))
                a+=6

            if b+11<len(values):
                onehourlist.append(getTempList(values,b,12))
                b+=12
        
        inc=len(values)-i
        if inc>0:
            fifminutelist.append(getTempList(values,i,inc))
        
        inc=len(values)-a
        if inc>0:
            thirminutelist.append(getTempList(values,a,inc))

        inc=len(values)-b
        if inc>0:
            onehourlist.append(getTempList(values,b,inc))

        writeToFile(fifminutelist,15,datafile)
        writeToFile(thirminutelist,30,datafile)
        writeToFile(onehourlist,60,datafile)
        progresscount+=1

def createDataForOtherHigherTimeFrames():
    global progresscount
    dataFiles=os.listdir(os.getcwd()+'/data120')
    for datafile in dataFiles:
        DF =    pd.read_csv(os.getcwd()+'/data120/{}'.format(datafile))
        values  =   DF.to_numpy()
        i=0
        a=0
        b=0

        fourhourlist=[]
        eighthourlist=[]
        onedaylist=[]
        while i+1<len(values):
            fourhourlist.append(getTempList(values,i,2))
            i+=2
            
            if a+3<len(values):
                eighthourlist.append(getTempList(values,a,4))
                a+=4

            if b+11<len(values):
                onedaylist.append(getTempList(values,b,12))
                b+=12

        inc=len(values)-i
        if inc>0:
            fourhourlist.append(getTempList(values,i,inc))
        
        inc=len(values)-a
        if inc>0:
            eighthourlist.append(getTempList(values,a,inc))

        inc=len(values)-b
        if inc>0:
            onedaylist.append(getTempList(values,b,inc))
        
        writeToFile(fourhourlist,240,datafile)
        writeToFile(eighthourlist,480,datafile)
        writeToFile(onedaylist,1440,datafile)
        progresscount+=1

def writeToFile(list,timeframe,datafile):
    DF=pd.DataFrame(np.asarray(list))
    os.makedirs(os.getcwd()+"/data"+str(timeframe), exist_ok=True)
    DF.to_csv(os.getcwd()+"/data"+str(timeframe)+"/"+datafile,line_terminator="\n\n")

def getTempList(values,i,inc):
    templist=[]
    opentime="{:.0f}".format(values[i][1])
    open ="{:.8f}".format(values[i][2])
    high= "{:.8f}".format(max(values[i:i+inc,3]))
    low=  "{:.8f}".format(min(values[i:i+inc,4]))
    close= "{:.8f}".format(values[i+inc-1][5])
    volume="{:.8f}".format(sum(values[i:i+inc,6]))
    
    templist.append(opentime)
    templist.append(open)
    templist.append(high)
    templist.append(low)
    templist.append(close)
    templist.append(volume)
    return templist

def updateDataForFiveMinutes(connectionClient):
    dataFiles=os.listdir(os.getcwd()+"/data5")
    for dataFile in dataFiles:
        t1=threading.Thread(target=updateFiveMinuteThread,args=[dataFile,connectionClient])
        while(int(connectionClient.response.headers['x-mbx-used-weight-1m'])+threading.active_count()*1.2>1140):
            connectionClient.ping()
            time.sleep(2)
        t1.start()
    createDataForOtherTimeFrames()

def updateFiveMinuteThread(dataFile,connectionClient):
    global progresscount
    fileLocation=os.getcwd()+"/data5/"+dataFile
    DF=pd.read_csv(fileLocation,dtype={"0":(np.unicode_),"1":str,"2":str,"3":str,"4":str,"5":str})
    startTime=int(DF.iloc[-1][1])
    DF.drop(index=DF.index[-1], axis=0, inplace=True)
    dfarray=DF.to_numpy()
    dfarray=np.delete(dfarray,0,axis=1)
    rows_to_delete=len(dfarray)-600
    if(rows_to_delete>12):
        dfarray=np.delete(dfarray,slice(int(rows_to_delete/12)*12),axis=0)
    symbol=dataFile.split(".")[0]
    while True:
        try:
            klines=connectionClient.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, startTime=startTime,endTime=int(time.time()*1000))
            break
        except:
            print("Retrying after 10 seconds")
            time.sleep(10)
    progresscount+=1
    # print(symbol,connectionClient.response.headers['x-mbx-used-weight-1m'])
    a=np.asarray(klines)
    if len(a)>1:
        a=np.delete(a,(6,7,8,9,10,11),1)
    elif len(a)==1:
        a=np.delete(a,(6,7,8,9,10,11))
        a=a[np.newaxis,:]
    else:
        return
    dfarray=np.concatenate((dfarray,a),axis=0)
    try:
        DF = pd.DataFrame(dfarray)
    except Exception as e:
        print(e)
        return
    DF.to_csv(fileLocation,line_terminator="\n\n",float_format='%.8f')

def updateDataForTwoHours(connectionClient):
    print("getting executed")
    dataFiles=os.listdir(os.getcwd()+"/data120")
    for dataFile in dataFiles:
        t1=threading.Thread(target=updateTwoHourThread,args=[dataFile,connectionClient])
        while(int(connectionClient.response.headers['x-mbx-used-weight-1m'])+threading.active_count()*1.2>1140):
            connectionClient.ping()
            time.sleep(2)
        t1.start()
    createDataForOtherHigherTimeFrames()

def updateTwoHourThread(dataFile,connectionClient):
    global progresscount
    fileLocation=os.getcwd()+"/data120/"+dataFile
    DF=pd.read_csv(fileLocation,dtype={"0":(np.unicode_),"1":str,"2":str,"3":str,"4":str,"5":str})
    startTime=int(DF.iloc[-1][1])
    DF.drop(index=DF.index[-1], axis=0, inplace=True)
    dfarray=DF.to_numpy()
    dfarray=np.delete(dfarray,0,axis=1)
    rows_to_delete=len(dfarray)-600
    if(rows_to_delete>12):
        dfarray=np.delete(dfarray,slice(int(rows_to_delete/12)*12),axis=0)
    symbol=dataFile.split(".")[0]
    while True:
        try:
            klines=connectionClient.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_2HOUR, startTime=startTime,endTime=int(time.time()*1000))
            break
        except:
            print("Retrying after 10 seconds")
            time.sleep(10)
    progresscount+=1
    a=np.asarray(klines)
    if len(a)>1:
        a=np.delete(a,(6,7,8,9,10,11),1)
    elif len(a)==1:
        a=np.delete(a,(6,7,8,9,10,11))
        a=a[np.newaxis,:]
    else:
        return
    dfarray=np.concatenate((dfarray,a),axis=0)
    try:
        DF = pd.DataFrame(dfarray)
    except Exception as e:
        print(e)
        return
    DF.to_csv(fileLocation,line_terminator="\n\n",float_format='%.8f')

def collectWeeklyData(allSymbols,connectionClient):
    startTime=int(time.time())-round(time.time())%604800-50*7*24*3600
    for symbol in allSymbols:
        sym = symbol[0:len(symbol)-1]
        while True:
            try:
                klines = connectionClient.get_klines(symbol=sym, interval=Client.KLINE_INTERVAL_1WEEK ,startTime=startTime*1000,endTime=time.time()*1000)
                break
            except:
                print("Retrying after 10 seconds")
                time.sleep(10)
        a=np.asarray(klines)
        try:
            DF = pd.DataFrame(np.delete(a,(6,7,8,9,10,11),1))
        except:
            continue
        os.makedirs(os.getcwd()+"/data10080", exist_ok=True)
        symDataFile = open(os.getcwd()+"/data10080/"+sym+".csv","w")
        DF.to_csv(symDataFile)
        symDataFile.close()

def updateWeeklyData(connectionClient):
    dataFiles=os.listdir(os.getcwd()+"/data10080")
    for dataFile in dataFiles:
        t1=threading.Thread(target=updateWeeklyDataThread,args=[dataFile,connectionClient])
        while(int(connectionClient.response.headers['x-mbx-used-weight-1m'])+threading.active_count()*1.2>1140):
            connectionClient.ping()
            time.sleep(5)
        t1.start()

def updateWeeklyDataThread(dataFile,connectionClient):
    global progresscount
    fileLocation=os.getcwd()+"/data10080/"+dataFile
    DF=pd.read_csv(fileLocation,dtype={"0":(np.unicode_),"1":str,"2":str,"3":str,"4":str,"5":str})
    startTime=int(DF.iloc[-1][1])
    DF.drop(index=DF.index[-1], axis=0, inplace=True)
    dfarray=DF.to_numpy()
    dfarray=np.delete(dfarray,0,axis=1)
    if(len(dfarray)>50):
        DF.drop(index=DF.index[0], axis=0, inplace=True)
    symbol=dataFile.split(".")[0]
    while True:
        try:
            klines=connectionClient.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1WEEK, startTime=startTime,endTime=int(time.time()*1000))
            break
        except:
            print("Retrying after 10 seconds")
            time.sleep(10)
    progresscount+=1
    a=np.asarray(klines)
    # print(symbol,connectionClient.response.headers['x-mbx-used-weight-1m'])
    if len(a)>1:
        a=np.delete(a,(6,7,8,9,10,11),1)
    elif len(a)==1:
        a=np.delete(a,(6,7,8,9,10,11))
        a=a[np.newaxis,:]
    else:
        return
    dfarray=np.concatenate((dfarray,a),axis=0)
    try:
        DF = pd.DataFrame(dfarray)
    except Exception as e:
        print(e)
        return
    DF.to_csv(fileLocation,line_terminator="\n\n",float_format='%.8f')

def showProgressBar(totalCount):
    global progresscount
    barCount=0
    with alive_bar(totalCount,ctrl_c=True,title="COLLECTING DATA    ") as bar:
        while progresscount<totalCount:
            for i in range(progresscount):
                if i<barCount:
                    continue
                bar()
                barCount+=1
            time.sleep(0.5)
        bar(totalCount-barCount)
        time.sleep(0.5)