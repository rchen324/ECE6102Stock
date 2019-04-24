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
from alpha_vantage.timeseries import TimeSeries
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from kafka.producer import SimpleProducer

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")

#Connect to Kafka
client = KafkaClient("ip-10-179-181-24.ec2.internal:6667")
producer = SimpleProducer(client)

def push_stock_price_to_Kafka(stock_name, days_num):
    topic_name = stock_name + "_stock"
    print "Downloading data from alpha vantage and publishing to " + stock_name + " topic"
    today = datetime.datetime.today()
    dateslist_datetime = [today - datetime.timedelta(days=x) for x in range(0, days_num)]
    dateslist = []
    for d in dateslist_datetime:
        d_str = d.strftime("%Y-%m-%d")
        dateslist.append(d_str)
    filename = "{}_data.csv".format(stock_name)
    ts = TimeSeries(key='OJC57JXH4SUQN338', output_format='csv')
    data = ts.get_intraday(symbol=stock_name, interval="60min", outputsize='full')
    #write data to corresoinding csv file
    i = 0
    for row in data:
        for r in row or []:
            if r[0].split(" ")[0] in dateslist:
                producer.send_messages('topicname', data)
    print "publishing finished"


get_stock_price_history("GOOGL", 4)
