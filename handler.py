import os
import urllib
import time
import datetime

from google.appengine.ext import ndb

import jinja2
import webapp2

today = datetime.datetime.today()
today_str = today.strftime("%Y-%m-%d")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Results(ndb.Model):
    "Recommendation results"
    date = ndb.StringProperty(indexed=True)
    rec = ndb.StringProperty(indexed=False)

class Covariance(ndb.Model):
    "Covariance Matrix for everyday"
    date = ndb.StringProperty(indexed=True)
    cov = ndb.StringProperty(indexed=False)

class getValues(webapp2.RequestHandler):
    def get(self):
        #covariance_query = Covariance.query(Results.date == today_str)
        #covariance_lis = covariance_query.fetch()

        #if covariance_lis:



        #results_query = Results.query(Results.date == today_str)
        results_query = Results.query()
        results_lis = results_query.fetch()

        template_values = None

        if results_lis:
            res_dict = eval(results_lis[0].rec)
            template_values = {
                'it':  res_dict['Stock'],
                'Return': res_dict['Return'],
                'Volatility': res_dict['Volatility'],
                'Sharpe': res_dict['Sharpe'],
            }
        else:
            template_values = {
                'it': {'Google': 1, 'MSFT':2}
            }

        template = JINJA_ENVIRONMENT.get_template('chart.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', getValues),
], debug=True)
