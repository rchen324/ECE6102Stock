import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from io import StringIO

import datetime

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")
stock_lis = ["GOOGL", "FB", "MSFT"]
filepath = "stocks/" + today_str + ".csv"

def calcMuCov(filepath):
    # Read in price data
    s = StringIO("date,GOOGL,FB,MSFT\n'2019-04-24', 1266.87, 183.39499999999998, 125.185\n'2019-04-23', 1263.2, 182.85, 124.705\n2019-04-22,1243.855,179.95749999999998,123.285")
    df = pd.read_csv(s, parse_dates=True, index_col="date")

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    return mu, S

def calcMuCov2(strIo):
    df = pd.read_csv(strIo, parse_dates=True, index_col="date")

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