
from configmanager import cmapi

def getDatasourceDays():
    site = cmapi.getItemValue('site', {})
    days = site.get('datasource.days', 7)
    return days

