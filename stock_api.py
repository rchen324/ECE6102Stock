"""
Author: Runfeng Chen

There are only two functions that the server should use directly: clear_files() and prediction_today()

Sample usage:
    1, when the directory does not contain pre-generated graphs and data csv for today, do:
            prediction_graph_name, training_graph_name, max, min, avg, trend = prediction_today("MSFT")

    2, when the directroty contains pre-generated graphs and data csv for today, but you want the model to be retrained, do:
            clear_files("MSFT")
            prediction_graph_name, training_graph_name, max, min, avg, trend = prediction_today("MSFT")

    3, when the directroty contains pre-generated graphs and data csv for today, but you want use those files again, do:
            prediction_graph_name, training_graph_name, max, min, avg, trend = prediction_today("MSFT")

Note: remember to install the required dependencies first
"""

import os
import csv
import time
import numpy as np
import datetime
from datetime import date
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from kafka import KafkaProducer
from alpha_vantage.timeseries import TimeSeries

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")
producer = KafkaProducer(bootstrap_servers='localhost:1234')

def stock_price(stock_name, days_num):
    avgs = []
    for s in stock_name:
        print ("Downloading data from alpha vantage for " + s)
        today = datetime.datetime.today()
        dateslist_datetime = [today - datetime.timedelta(days=x) for x in range(0, days_num)]
        dateslist = []
        for d in dateslist_datetime:
            d_str = d.strftime("%Y-%m-%d")
            dateslist.append(d_str)
        #filename = "{}_data.csv".format(stock_name)
        ts = TimeSeries(key='OJC57JXH4SUQN338', output_format='csv')
        data = ts.get_daily(symbol=s)
        print (data)
        producer.send('foobar', b'some_message_bytes')
        #write data to corresoinding csv file
        i = 0
        prices = 0
        for row in data:
            for r in row or []:
                if r[0].split(" ")[0] in dateslist:
                    i += 1
                    prices += (float(r[2]) + float(r[3])) / 2.0
                    print (r)
        avg = prices / float(i)
        avgs.append((s, avg))
        print ("Downloading finished for " + s)
    print (avgs)

if __name__ == "__main__":
    first = True
    while True:
        if first:
            stock_price(["GOOGL", "FB", "MSFT"], 30)
            first = False
            time.sleep(86400)
        else:
            stock_price(["GOOGL", "FB", "MSFT"], 1)



