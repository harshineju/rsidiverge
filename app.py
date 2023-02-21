import multiprocessing
from flask import Flask, render_template, request, redirect
from main1 import collectData1,checkCupAndHandle
from dataHandler import checkForBearishDivergence, checkForBullishDivergence
from main1 import createSymbolFile, getLastModified
import config
from binance.client import Client
from binance.enums import *
from flask_cors   import CORS,cross_origin
import pandas
import os
import talib
from patterns import candlestick_patterns
from RSICROSSING import checkRsiCrossed
import time
import pickle

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
client = Client(config.API_KEY, config.API_SECRET)

startTime=0
ct1=multiprocessing.Process(target=collectData1,args=[client])
@app.route('/')
def index():
    title = "ASHOK'S RSI DIVERGENCE"
    timeFrame       =   request.args.get('timef',"")
    divergenceType  =   request.args.get('type',"")
    result=[]
    if not timeFrame=="":
        if divergenceType=='bullish':
            result=checkForBullishDivergence(timeFrame)
        else:
            result=checkForBearishDivergence(timeFrame)
    else:
        if os.path.isfile(os.getcwd()+"/divergenceResults/bullish.csv"):
            if divergenceType=='bullish':
                file = open(os.getcwd()+"/divergenceResults/bullish.csv","rb")
                result=pickle.load(file)
                file.close()
            elif divergenceType=='bearish':
                file = open(os.getcwd()+"/divergenceResults/bearish.csv","rb")
                result=pickle.load(file)
                file.close()
    lastTime=getLastModified()
    return render_template('index.html', title=title,results=result,lastTime=lastTime)

@app.route('/rsiCrossing')
def rsiCrossing():
    divergenceType  =   request.args.get("type","bullish")
    crossingValue   =   request.args.get("crossValue")
    result=checkRsiCrossed(divergenceType,crossingValue)
    lastTime=getLastModified()
    return render_template('rsiCrossing.html',results=result,lastTime=lastTime)

@app.route('/patterns')
def patterns():
    pattern  = request.args.get('pattern', False)
    timeframe= request.args.get('timef',False)
    stocks={}
    if pattern and timeframe:
        allSymbols=createSymbolFile(client)
        # collectData(allSymbols,timeframe,client)
        for dataFile in os.listdir(os.getcwd()+'/data{}'.format(timeframe)):
            df = pandas.read_csv(os.getcwd()+'/data{}/{}'.format(timeframe,dataFile))
            pattern_function = getattr(talib, pattern)
            values = df.to_numpy()
            symbol = dataFile.split('.')[0]
            stocks[symbol] = {'symbol': symbol}
            try:
                results = pattern_function(values[:,2], values[:,3], values[:,4], values[:,5])
                last = results[len(results)-1]
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print("error")
    return render_template('patterns.html', candlestick_patterns=candlestick_patterns, stocks=stocks, pattern=pattern)

@app.route('/collectData')
def collectdata():
    global startTime,ct1
    if time.time()-startTime>300:
        if ct1.is_alive():
            ct1.terminate()
            ct1=multiprocessing.Process(target=collectData1,args=[client])
        ct1.start()
        startTime=time.time()
    else:
        print("Already collecting")
    return redirect("/")

@app.route('/cupAndHandle')
def cupAndHandle():
    result=checkCupAndHandle()
    lastTime=getLastModified()
    return render_template('rsiCrossing.html',results=result,lastTime=lastTime)