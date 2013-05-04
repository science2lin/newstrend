from commonutil import dateutil
import configmanager.models
from configmanager import cmapi

import globalconfig

class LatestItem(configmanager.models.ConfigItem):
    pass

class DisplayItem(configmanager.models.ConfigItem):
    pass

cmapi.registerModel(LatestItem)
cmapi.registerModel(DisplayItem)

def receiveData(datasource, items):
    if datasource.get('charts'):
        keyname = 'chartses'
    else:
        keyname = 'sites'
    _saveDatasource(datasource, items, keyname)

def _saveDatasource(datasource, items, keyname):
    datasources = cmapi.getItemValue(keyname, [], modelname=LatestItem)

    days = globalconfig.getDatasourceDays()
    strStart = dateutil.getHoursAs14(days * 24)
    datasources = [child for child in datasources
                    if child['source']['added'] >= strStart]

    data = {
        'source': datasource,
        'pages': items,
    }

    foundIndex = -1
    for i in range(len(datasources)):
        item = datasources[i]
        if item['source'].get('slug') == datasource.get('slug'):
            foundIndex = i
            break
    if foundIndex >= 0:
        datasources[foundIndex] = data
    else:
        datasources.append(data)
    cmapi.saveItem(keyname, datasources, modelname=LatestItem)

