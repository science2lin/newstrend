
from configmanager import cmapi

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
    if 'psegs' not in result:
        # result['psegs'] = ['n', 'ns', 'nr', 'eng']
        result['psegs'] = []
    return result

def getStopWords():
    return cmapi.getItemValue('words.stop', [])

def getWordsDict():
    return cmapi.getItemValue('words.dict', [])

