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
    date = ndb.StringProperty(indexed=False)
    recommendation = ndb.StringProperty(indexed=False)

class Covariance(ndb.Model):
    "Covariance Matrix for everyday"
    date = ndb.StringProperty(indexed=False)
    covariance = ndb.StringProperty(indexed=False)

class getValues(webapp2.RequestHandler):
    def get(self):
        covariance_query = Covariance.query(Results.date == today_str)
        covariance = covariance_query.fetch()

        results_query = Results.query(Results.date == today_str)
        results = results_query.fetch()
        template_values = {
            'it': results,
            'covariance': covariance
        }
        template = JINJA_ENVIRONMENT.get_template('chart.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/chart', getValues),
], debug=True)
