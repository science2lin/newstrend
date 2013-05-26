import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import networkutil
from . import models

class WordsRequest(webapp2.RequestHandler):

    def post(self):
        data = json.loads(self.request.body)
        models.saveWordsRequest(data['key'], data)
        backendsData = json.dumps({'key': data['key']})
        taskqueue.add(queue_name="words", payload=backendsData, url='/backends/run/')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Request is accepted.')

