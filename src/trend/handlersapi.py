import json
import logging

from google.appengine.api import taskqueue

import webapp2

from commonutil import networkutil
from . import models

class WordsRequest(webapp2.RequestHandler):

    def post(self):
        data = json.loads(self.request.body)
        uuid = data.get('uuid')
        if networkutil.isUuidHandled(uuid):
            message = 'WordsRequest: %s is already handled.' % (uuid, )
            logging.warn(message)
            self.response.out.write(message)
            return
        networkutil.updateUuids(uuid)

        sourceapp = self.request.headers.get('app')
        if sourceapp:
            key = sourceapp + '.' + data['key']
        else:
            key = data['key']
        models.saveWordsRequest(key, data)
        backendsData = json.dumps({'key': key})
        taskqueue.add(queue_name="words", payload=backendsData, url='/backends/run/')
        self.response.headers['Content-Type'] = 'text/plain'
        message = 'Request for %s is accepted.' % (key, )
        logging.info(message)
        self.response.out.write(message)

