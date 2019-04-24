import flask
from flask import request, render_template, jsonify
import boto3
import cPickle as pickle
import time
import json
import stock_api
import os
import math

# Get this file's path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Read config
with open('config.json') as config_data:
    config = json.load(config_data)

# Create the application.
APP = flask.Flask(__name__)

#Enter AWS Credentials
AWS_KEY=config['aws']['key']
AWS_SECRET=config['aws']['secret']
REGION="us-east-2"

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_KEY,
                            aws_secret_access_key=AWS_SECRET,
                            region_name=REGION)
msft_table = dynamodb.Table('MSFT')
fb_table = dynamodb.Table('FB_stock')
googl_table = dynamodb.Table('GOOGL')

################################################################################
@APP.route('/stock/<string:stock_name>')
def render_stock(stock_name):
    # Get graph data for stock
    pred_graph_name, train_graph_name, stock_max, stock_min, avg, trend = stock_api.prediction_today(stock_name)
    # Pass graph file names to HTML doc
    path_name1, pred_name = pred_graph_name.split('/')
    path_name2, train_name = train_graph_name.split('/')

    if (stock_name == "MSFT"):
        data = msft_table.scan()
    elif (stock_name == "GOOGL"):
        data = googl_table.scan()
    elif (stock_name == "FB"):
        data = fb_table.scan()

    # Calculate average sentiment with log multiplier on followers
    rows = data['Items']
    sentiment_sum = 0
    total_rows = len(rows)
    for row in rows:
        weighted = float(row['prediction']) * math.log(float(row['followers']) + 3)
        sentiment_sum = sentiment_sum + weighted
    average_sentiment = sentiment_sum / total_rows

    # Compute recommendation to buy
    if (trend == "Increase" and average_sentiment > 0):
        recommendation = "Yes"
    elif (trend == "Increase" and average_sentiment < 0):
        recommendation = "Probably not"
    elif (trend == "Decrease" and average_sentiment > 0):
        recommendation = "Probably yes"
    elif (trend == "Decrease" and average_sentiment < 0):
        recommendation = "No"
    else:
        recommendation = "Not enough information"

    return render_template('stock_page.html', title=stock_name, pred=pred_name, train=train_name, sent=average_sentiment, rec=recommendation)
################################################################################
@APP.route('/tweet/<string:stock_name>')
def render_tweets(stock_name):

    if (stock_name == "MSFT"):
        results = msft_table.scan()
    elif (stock_name == "GOOGL"):
        results = googl_table.scan()
    elif (stock_name == "FB"):
        results = fb_table.scan()

    html = '<html><body><table width=80% border=1 align="center">'+\
            '<tr><td><strong>Timestamp</strong></td><td><strong>Tweet</strong></td><td><strong>Sentiment</strong></td><td><strong>Followers</strong></td></tr>'

    for result in results['Items']:
        html+='<tr><td>'+result['timestamp']+'</td><td>'+result['data']+'</td><td>'+str(result['prediction'])+'</td><td>'+str(result['followers'])+'</td></tr>'


    html+='</table></body></html>'

    return html

################################################################################
@APP.route('/retrain')
def retraining():
    stock_api.clear_files("MSFT")
    stock_api.clear_files("GOOGL")
    stock_api.clear_files("FB")
    return render_template('refresh.html')

################################################################################
@APP.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    APP.debug=True
    APP.run(host='0.0.0.0', port=5000)
