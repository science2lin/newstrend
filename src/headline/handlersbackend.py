import datetime
import logging

from google.appengine.api import taskqueue
import webapp2

from pytz.gae import pytz

from commonutil import networkutil
import globalconfig
from hotword import hwapi
from . import models, bs

class Start(webapp2.RequestHandler):

    def get(self):
        if not self.request.get('force') and not isBackendsTime():
            logging.info('Now is not backends time.')
            return
        taskqueue.add(queue_name='words', url='/backends/run/')


def isBackendsTime():
    _INTERVAL_MINUTES = 5
    backendsConfig = globalconfig.getBackendsConfig()
    if not backendsConfig:
        return True

    timezonename = backendsConfig.get('timezone')
    if not timezonename:
        return True

    freeHours = backendsConfig.get('hours.free', [])
    limitHours = backendsConfig.get('hours.limit', [])

    if not freeHours and not limitHours:
        return True

    nnow = datetime.datetime.now(tz=pytz.utc)
    tzdate = nnow.astimezone(pytz.timezone(timezonename))

    if tzdate.hour in freeHours:
        return True

    if tzdate.hour in limitHours and tzdate.minute < _INTERVAL_MINUTES:
        return True

    return False

def _runTask():
    wordsConfig = globalconfig.getWordsConfig()
    stopWords = globalconfig.getStopWords()
    wordsData = {}

    sitePages = models.getPages(keyname='sites')
    siteWords = hwapi.calculateTopWords(wordsConfig, stopWords, 'sites', sitePages)
    wordsData['sites'] = siteWords

    pages = models.getPages(keyname='chartses')
    chartsWords = hwapi.calculateTopWords(wordsConfig, stopWords, 'chartses', pages)
    wordsData['chartses'] = chartsWords

    channels = models.getChannels()
    channelsWords = {}
    for channel in channels:
        slug = channel.get('slug')
        if not slug:
            continue
        tags = channel.get('tags')
        if not tags:
            continue
        channelPages = bs.getPagesByTags(sitePages, tags)
        if not channelPages:
            continue
        channelWords = hwapi.calculateTopWords(wordsConfig, stopWords, slug, channelPages)
        channelsWords[slug] = channelWords
    wordsData['channels'] = channelsWords

    callbackurl = globalconfig.getMasterUrl()
    _URL_TIMEOUT = 30
    _CALLBACK_TRYCOUNT = 3
    if callbackurl:
        success = networkutil.postData(callbackurl, wordsData, tag='words backend',
                    trycount=_CALLBACK_TRYCOUNT, timeout=_URL_TIMEOUT)
        if success:
            message = 'Post words successfully.'
        else:
            message = 'Failed to post words.'
        logging.info(message)
    else:
        logging.warn('No master url is available.')


class Run(webapp2.RequestHandler):

    def post(self):
        try:
            _runTask()
        except Exception:
            logging.exception('Failed to execute _calculateWords.')

