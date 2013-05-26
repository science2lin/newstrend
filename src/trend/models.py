import configmanager.models
from configmanager import cmapi

class WordsRequest(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(WordsRequest)

def saveWordsRequest(keyname, data):
    cmapi.saveItem(keyname, data, modelname=WordsRequest)

def getWordsRequest(keyname):
    value = cmapi.getItemValue(keyname, modelname=WordsRequest)
    cmapi.removeItem(keyname, modelname=WordsRequest)
    return value


