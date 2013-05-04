from commonutil import collectionutil

def _isPageMatched(pageTags, tags):
    matched = False
    for tag in tags:
        if collectionutil.fullContains(pageTags, tag.split('+')):
            matched = True
            break
    return matched

def getPagesByTags(pages, tags, returnMatched=True):
    result = []
    for page in pages:
        pageTags = page['source']['tags']
        matched = _isPageMatched(pageTags, tags)
        if (returnMatched and matched) or (not returnMatched and not matched):
            result.append(page)
    return result

