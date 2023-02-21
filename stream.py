import os
from attr import NOTHING
from flask import jsonify
import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import main1
import sys,time

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

in_position = False
mainlist=[]

client = Client(config.API_KEY, config.API_SECRET)
    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    ws.run_forever()

def on_message(ws, message):
    global in_position, mainlist
    print('received message size')
    print(ws,sys.getsizeof(message))
    json_message = json.loads(message)
    print(json_message)
    # file = open(os.getcwd()+"/jsonFile.csv","w")
    # file.write(str(json_message))
    # file.close()
    time.sleep(26)
    # # pprint.pprint(json_message)
    # candle = json_message['k']
    # is_candle_closed = candle['x']

    # if is_candle_closed:
    #     candlelist=[]
    #     time=candle['t']
    #     open=candle['o']
    #     high=candle['h']
    #     low=candle['l']
    #     close = candle['c']
    #     volume=candle['v']
    #     candlelist.append(time)
    #     candlelist.append(open)
    #     candlelist.append(high)
    #     candlelist.append(low)
    #     candlelist.append(close)
    #     candlelist.append(volume)

    #     mainlist.append(candlelist)
    # print(mainlist)

def openWebSockets():
    allSymbols=main1.createSymbolFile(client)
    SOCKET= "wss://stream.binance.com:9443/ws"
    i=True
    for sym in allSymbols:
        symbol=sym[0:len(sym)-1]
        symbol=symbol.lower()
        SOCKET+="/"+symbol+"@kline_5m"
        SOCKET+="/"+symbol+"@kline_2h"
        # if not i:
        #     break
        # else: i=False
    print(SOCKET)
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()

openWebSockets()