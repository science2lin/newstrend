# coding=utf-8
import logging
import re

def _isStopWord(stopWordPatterns, word):
    stopped = False
    for pattern in stopWordPatterns:
        if re.match(pattern, word, re.IGNORECASE|re.DOTALL):
            stopped = True
            break
    return stopped

def getTopWords(psegs, titles, stopWordPatterns, stopWords):
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
    return result

def _getWordTitles(titles, words):
    result = {}
    for word in words:
        wordTitles = set()
        for title in titles:
            if word['name'] in title:
                wordTitles.add(title)
        word['weight'] = len(wordTitles)
        result[word['name']] = wordTitles
    return result

def _isSimilarWords(similarCriterion, parentTitles, childTitles):
    total = len(childTitles)
    common = len(childTitles.intersection(parentTitles))
    if common == total:
        return True
    if not similarCriterion:
        return False
    threshhold = similarCriterion.get('0')
    if common >= threshhold:
        return True
    threshhold = similarCriterion.get(str(total))
    if not threshhold:
        return False
    return common >= threshhold

def _mergeWords(similarCriterion, titles, words):
    wordTitles = _getWordTitles(titles, words)
    index = 0
    size = len(words)
    while index < size:
        word = words[index]
        index2 = index + 1
        children = []
        parentTitles = wordTitles[word['name']]
        while index2 < size:
            word2 = words[index2]
            childTitles = wordTitles[word2['name']]
            if len(childTitles) == 0:
                logging.warn('Empty child: %s' % (word2))
                index2 += 1
                continue
            if _isSimilarWords(similarCriterion, parentTitles, childTitles):
                parentTitles.update(childTitles)
                word['weight'] = len(parentTitles)
                del wordTitles[word2['name']]
                children.append(word2)
                del words[index2]
                size -= 1
                # the previous may be mergable after parent titles grow.
                index2 = index + 1
            else:
                index2 += 1
        if children:
            children.sort(key=lambda item: item['weight'], reverse=True)
            word['children'] = children
        index += 1

def _populateWords(psegs, stopWordPatterns, stopWords, similarCriterion, titles):
    words = getTopWords(psegs, titles, stopWordPatterns, stopWords)
    _mergeWords(similarCriterion, titles, words)
    return words

def calculateWords(wordsConfig, stopWords, titles):
    stopWordPatterns = wordsConfig['stop.patterns']
    similarCriterion = wordsConfig['similar']
    psegs = wordsConfig['psegs']

    allWords = _populateWords(psegs, stopWordPatterns, stopWords, similarCriterion, titles)
    return allWords

