# coding=utf-8
import copy
import logging
import re

def _isStopWord(stopWordPatterns, word):
    stopped = False
    for pattern in stopWordPatterns:
        if re.match(pattern, word, re.IGNORECASE|re.DOTALL):
            stopped = True
            break
    return stopped

def _getTopWords(psegs, titles, stopWordPatterns, stopWords, userDict):
    content = '\n'.join(titles)

    import jieba # May fail to load jieba
    if psegs:
        jieba.initialize(usingSmall=True)
        import jieba.posseg as pseg
        pseg.loadDictModel(usingSmall=True)
        pwords = []
        flags = psegs
        for word in pseg.cut(content):
            if word.flag not in flags:
                continue
            pwords.append(word.word)
    else:
        jieba.initialize(usingSmall=False)
        if userDict:
            jieba.load_userdict_items(userDict)
        pwords = jieba.cut(content, cut_all=False)

    words = []
    for word in pwords:
        # sometime "\r\n\n" encountered
        word = word.strip()
        if not word:
            continue
        if word in stopWords:
            continue
        if _isStopWord(stopWordPatterns, word):
            continue
        words.append(word)
    words.sort()

    lastWord = None
    lastCount = 0
    result = []
    _MIN_WORD_COUNT = 2
    for word in words:
        if lastWord != word:
            if lastCount >= _MIN_WORD_COUNT:
                result.append({'name': lastWord, 'count': lastCount})
            lastWord = word
            lastCount = 0
        lastCount += 1
    if lastCount >= _MIN_WORD_COUNT:
        result.append({'name': lastWord, 'count': lastCount})

    result.sort(key=lambda item: len(item['name']), reverse=True)
    result.sort(key=lambda item: item['count'], reverse=True)
    return [ item['name'] for item in result ]

def _getWordTitles(titles, words):
    result = []
    for word in words:
        wordTitles = set()
        for title in titles:
            if word in title:
                wordTitles.add(title)
        result.append({
            'name': word,
            'titles': wordTitles,
            'children': [],
        })
    return result

def _mergeWords(wordTitles):
    for word in wordTitles:
        if 'merged' in word:
            del word['merged']
    i =  0
    size = len(wordTitles)
    while i < size - 1:
        if 'merged' in wordTitles[i]:
            i += 1
            continue
        j = i + 1
        while j < size:
            if wordTitles[i]['titles'].issuperset(wordTitles[j]['titles']):
                wordTitles[i]['children'].append(copy.deepcopy(wordTitles[j]))
                wordTitles[j]['merged'] = True
            j += 1
        i += 1
    return [ word for word in wordTitles if 'merged' not in word ]

def _collectWord(result, mainNames, word={}, children=[]):
    _MIN_SIZE = 2
    keywords = []
    for item in mainNames:
        keywords.append(item)
    if word:
        keywords.append(word['name'])
    for item in word.get('children') or children:
        keywords.append(item['name'])
    if len(keywords) >= _MIN_SIZE:
        result.append(keywords)

def _identifyWordGroup(result, mainNames, wordTitles):
    mWords = _mergeWords(wordTitles)
    _BIG_WORD = 4
    simpleChildren = []
    for word in mWords:
        if mainNames and not word['children']:
            simpleChildren.append(word)
            continue
        if len(word['children']) < _BIG_WORD:
            _collectWord(result, mainNames, word=word)
            continue
        _identifyWordGroup(result, mainNames + [word['name']], word['children'])
    if mainNames and simpleChildren:
        _collectWord(result, mainNames, children=simpleChildren)

def calculateWords(wordsConfig, stopWords, userDict, titles):
    stopWordPatterns = wordsConfig['stop.patterns']
    psegs = wordsConfig['psegs']

    words = _getTopWords(psegs, titles, stopWordPatterns, stopWords, userDict)
    wordTitles = _getWordTitles(titles, words)
    wordTitles.sort(key=lambda word: len(word['titles']), reverse=True)

    result = []
    _identifyWordGroup(result, [], wordTitles)

    return result

