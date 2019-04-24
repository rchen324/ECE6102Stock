import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

import datetime
from alpha_vantage.timeseries import TimeSeries

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")
stock_lis = ["GOOGL", "FB", "MSFT"]
filepath = "stocks/" + today_str + ".csv"

def pull_stock_price(stock_name, days_num):
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

def calcMuCov(filepath):
    # Read in price data
    df = pd.read_csv(filepath, parse_dates=True, index_col="date")

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    return mu, S

def maxSharpeRatio(mu, S):
    # Optimise for maximal Sharpe ratio
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    perf = ef.portfolio_performance(verbose=True)
    return cleaned_weights, perf

def combineWeigPerf(cleaned_weights, perf):
    result = {}
    result['Stock'] = cleaned_weights
    result['Return'] = perf[0]
    result['Volatility'] = perf[1]
    result['Sharpe'] = perf[2]
    return result

if __name__ == "__main__":
    #pull_stock_price(stock_lis, 30)
    mu, S = calcMuCov(filepath)
    cleaned_weights, perf = maxSharpeRatio(mu, S)
    result = combineWeigPerf(cleaned_weights, perf)
    print (result)