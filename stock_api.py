import os
import csv
import time
import datetime
from datetime import date
<<<<<<< HEAD
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from kafka import KafkaProducer
=======
>>>>>>> 7b6ee80940020e7b1197865eff89a1258cd439f4
from alpha_vantage.timeseries import TimeSeries

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")
producer = KafkaProducer(bootstrap_servers='localhost:1234')

def stock_price(stock_name, days_num):
    avgs = []
    row_num = days_num + 1
    column_num = len(stock_name) + 1
    avgs = [[0 for x in range(column_num)] for y in range(row_num)]
    for s in stock_name:
        print ("Downloading data from alpha vantage for " + s)
        today = datetime.datetime.today()
        dateslist_datetime = [today - datetime.timedelta(days=x) for x in range(0, days_num)]
        dateslist = []
        for d in dateslist_datetime:
            d_str = d.strftime("%Y-%m-%d")
            dateslist.append(d_str)
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

