import datetime
import json
import logging

import webapp2

from pytz.gae import pytz

from commonutil import networkutil
from . import models, bs, globalconfig

_URL_TIMEOUT = 30
_CALLBACK_TRYCOUNT = 3

def _runTask(requestData):
    wordsConfig = globalconfig.getWordsConfig()
    stopWords = globalconfig.getStopWords()
    userDict = globalconfig.getWordsDict()
    wordsData = bs.calculateWords(wordsConfig, stopWords, userDict, requestData['titles'])

    if not wordsData:
        logging.warn('No words is available for %s.' % (requestData['key'], ))
        return

    _TOP_WORD_COUNT = 20
    responseData = {
        'key': requestData['key'],
        'words': wordsData[:_TOP_WORD_COUNT],
    }
    masterUrls = requestData['masters']
    for callbackurl in masterUrls:
        success = networkutil.postData(callbackurl, responseData, tag='words backend',
                    trycount=_CALLBACK_TRYCOUNT, timeout=_URL_TIMEOUT)
        if success:
            message = 'Post words to %s for %s successfully.' % (callbackurl, requestData['key'], )
        else:
            message = 'Failed to post words to %s for %s.' % (callbackurl, requestData['key'], )
        logging.info(message)


class Run(webapp2.RequestHandler):

    def post(self):
        data = json.loads(self.request.body)
        key = data['key']
        requestData = models.getWordsRequest(key)
        try:
            _runTask(requestData)
        except Exception:
            logging.exception('Failed to execute _calculateWords.')

