import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

import datetime
#from alpha_vantage.timeseries import TimeSeries

from google.cloud import datastore
datastore_client = datastore.Client()

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")
stock_lis = ["GOOGL", "FB", "MSFT"]
filepath = "stocks/" + today_str + ".csv"

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
    
    kind = 'Results'
    name = 'result_'+today_str
    task_key = datastore_client.key(kind, name)

    task = datastore.Entity(key=task_key)
    task['date'] = today_str
    task['rec'] = str(result)
    datastore_client.put(task)

    print (result)
    

