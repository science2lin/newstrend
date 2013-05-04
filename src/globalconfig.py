
from configmanager import cmapi

def getDatasourceDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.days', 7)
    return days

def getMasterUrl():
    site = cmapi.getItemValue('site', {})
    url = site.get('master.url')
    return url

def getBackendsConfig():
    return cmapi.getItemValue('backends', {})

def getWordsConfig():
    result = cmapi.getItemValue('words', {})
    if 'stop.patterns' not in result:
        result['stop.patterns'] = []
    if 'similar' not in result:
        result['similar'] = {
                '0': 6
            }
    if 'hours.all' not in result:
        result['hours.all'] = 24
    if 'hours.latest' not in result:
        result['hours.latest'] = 4
    return result

def getStopWords():
    return cmapi.getItemValue('words.stop', [])

def getWordsDict():
    return cmapi.getItemValue('words.dict', [])

