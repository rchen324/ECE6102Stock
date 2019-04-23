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

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")

def clear_files(stock_name):
    prediction_graph_name = "static/{}_{}.png".format(stock_name, today_str)
    training_graph_name = "static/{}_{}_training.png".format(stock_name, today_str)
    datafile_name = "csv/{}_{}_data.csv".format(stock_name, today_str)
    if (os.path.exists(prediction_graph_name)):
        os.remove(prediction_graph_name)
    if (os.path.exists(training_graph_name)):
        os.remove(training_graph_name)
    if (os.path.exists(datafile_name)):
        os.remove(datafile_name)
    print "{} files removed".format(stock_name)


def prediction_today(stock_name):
    prediction_graph_name = "static/{}_{}.png".format(stock_name, today_str)
    training_graph_name = "static/{}_{}_training.png".format(stock_name, today_str)
    datafile_name = "csv/{}_{}_data.csv".format(stock_name, today_str)
    if (os.path.exists(prediction_graph_name) and os.path.exists(datafile_name) and os.path.exists(training_graph_name)):
        datafile = open(datafile_name, 'rb')
        datareader = csv.reader(datafile, delimiter = ",")
        max = float(next(datareader)[0])
        min = float(next(datareader)[0])
        avg = float(next(datareader)[0])
        trend = str(next(datareader)[0])
        datafile.close()
        return prediction_graph_name, training_graph_name, max, min, avg, trend
    else:
        get_stock_price_history(stock_name, 40)
        print "Building model"
        max, min, avg, trend = build_model(stock_name)
        print "Prediction Done"
        return prediction_graph_name, training_graph_name, max, min, avg, trend

def get_stock_price_history(stock_name, days_num):
    print "Downloading data from alpha vantage"
    today = datetime.datetime.today()
    dateslist_datetime = [today - datetime.timedelta(days=x) for x in range(0, days_num)]
    dateslist = []
    for d in dateslist_datetime:
        d_str = d.strftime("%Y-%m-%d")
        dateslist.append(d_str)
    filename = "{}_data.csv".format(stock_name)
    data_file = open(filename, "wb")
    writer = csv.writer(data_file, delimiter=',')
    #get the data through Alpha_Vantage API
    ts = TimeSeries(key='OJC57JXH4SUQN338', output_format='csv')
    data = ts.get_intraday(symbol=stock_name, interval="60min", outputsize='full')
    #write data to corresoinding csv file
    i = 0
    for row in data:
        for r in row or []:
            if r[0].split(" ")[0] in dateslist:
                writer.writerow(r)
    data_file.close()
    print "Downloading finished"

def create_data_sets(stock_name):
    print "creating training and testing sets"
    dates = []
    prices = []
    filename = "csv/{}_data.csv".format(stock_name)
    stock_file = open(filename, 'rb')
    stock_reader = csv.reader(stock_file, delimiter = ",")
    i = 0
    for row in stock_reader:
        dates.append(i)
        i += 1
        avg_price = (float(row[2]) + float(row[3])) / 2.0
        prices.append(avg_price)
    #aplit into training and testing data set
    training_dates, testing_dates, training_prices, testing_prices = train_test_split(dates, prices, test_size = 0.2)
    training_dates_array = np.reshape(training_dates, len(training_dates), 1).reshape(-1, 1)
    testing_dates_array = np.reshape(testing_dates, len(testing_dates), 1).reshape(-1, 1)
    training_prices_array = np.reshape(training_prices, len(training_prices), 1)
    testing_prices_array = np.reshape(testing_prices, len(testing_prices), 1)
    stock_file.close()
    print "Data sets created"
    return training_dates_array, testing_dates_array, training_prices_array, testing_prices_array

def build_model(stock_name):
    training_dates, testing_dates, training_prices, testing_prices = create_data_sets(stock_name)
    # Polynomial regression
    poly = PolynomialFeatures(degree=7)
    poly_training_dates = poly.fit_transform(training_dates)
    poly_testing_dates = poly.fit_transform(testing_dates)
    lin = LinearRegression(n_jobs=-1)
    #model training
    start_time = time.time()
    print "--------Training Starts--------"
    lin.fit(poly_training_dates, training_prices)
    print "--------Training Ends----------"
    end_time = time.time()
    training_time = end_time - start_time
    print "Summary: Time to train model is " + str(training_time) + "\n"
    #model testing
    start_time = time.time()
    print "--------Testing Starts--------"
    r2 = lin.score(poly_testing_dates, testing_prices)  # returns the coefficients of determination of the predictions
    print "--------Testing Ends----------"
    end_time = time.time()
    testing_time = end_time - start_time
    print "Summary: Time to test model is " + str(testing_time)
    print "Summary: Your model scored " + str(r2) + "\n"

    #visualize the training result
    #sort the tesing data first so that the result can be printed correctly
    poly_testing_dates.sort(axis=0)
    print "Plotiing the training result......"
    plt.figure(0)
    plt.scatter(training_dates, training_prices, color="black", label="Training Data")
    plt.scatter(testing_dates, testing_prices, color="blue", label="Testing Data")
    plt.plot(poly_testing_dates[:,1], lin.predict(poly_testing_dates), color="red", label="Model")
    plt.xlabel("Time")
    plt.ylabel("Stock Prices")
    plt.title("Training data graph")
    plt.legend()
    figname = "static/{}_{}_training.png".format(stock_name, today_str)
    print "Saving your training figure to " + figname
    plt.savefig(figname)
    plt.clf()
    plt.close()
    print "Training figure saved"
    #plt.show()

    #Make prediction for today
    prediction_time = []
    filename = "csv/{}_data.csv".format(stock_name)
    stock_file = open(filename, 'rb')
    stock_reader = csv.reader(stock_file, delimiter = ",")
    row_count = sum(1 for row in stock_reader) - 1
    for i in range(0, 7):
        curr_time = row_count + i
        prediction_time.append(curr_time)
    prediction_time = np.reshape(prediction_time, len(prediction_time), 1).reshape(-1, 1)
    prediction_time_poly = poly.fit_transform(prediction_time)
    prediction_prices = lin.predict(prediction_time_poly)
    stock_file.close()
    #write max, min, avg and trend to another csv for future use
    print "Saving max, min, avg and trend"
    max_price = max(prediction_prices)
    min_price = min(prediction_prices)
    avg_price = np.mean(prediction_prices)
    if (prediction_prices[0] > prediction_prices[-1]):
        trend = "Decrease"
    elif (prediction_prices[0] < prediction_prices[-1]):
        trend = "Increase"
    else:
        trend = "Flat"
    datafile_name = "csv/{}_{}_data.csv".format(stock_name, today_str)
    data_file = open(datafile_name, "wb")
    writer = csv.writer(data_file, delimiter=',')
    writer.writerow([max_price])
    writer.writerow([min_price])
    writer.writerow([avg_price])
    writer.writerow([trend])
    data_file.close()
    print "Saving done"

    #visualize the prediction result
    plt.figure(1)
    times = ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30"]
    plt.xticks(prediction_time_poly[:,1], times)
    plt.plot(prediction_time_poly[:,1], prediction_prices, color="red", label="Model")
    plt.xlabel("Time")
    plt.ylabel("Stock Prices")
    plt.title("Predict price for "  + stock_name + " today")
    #plt.legend()
    figname = "static/{}_{}.png".format(stock_name, today_str)
    print "Saving your prediction figure"
    plt.savefig(figname)
    plt.clf()
    plt.close()
    print "Prediction figure saved"
    #plt.show()
    return max_price, min_price, avg_price, trend

get_stock_price_history("GOOGL", 4)
