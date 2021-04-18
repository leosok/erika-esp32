
# -*- coding: utf-8 -*-
#
# Extracted from: https://github.com/micropython/micropython-lib/blob/master/urllib.parse/urllib/parse.py
#
import gc

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

def quote(s):
    res = []
    replacements = {}
    for c in s:
        if c in always_safe:
            res.append(c)
            continue
        res.append('%%%x' % ord(c))
        gc.collect()
    return ''.join(res)

def quote_plus(s):
    if ' ' in s:
        s = s.replace(' ', '+')
    return quote(s)

def unquote(s):
    """Kindly rewritten by Damien from Micropython"""
    """No longer uses caching because of memory limitations"""
    res = s.split('%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def unquote_plus(s):
    """unquote('%7e/abc+def') -> '~/abc def'"""
    s = s.replace('+', ' ')
    return unquote(s)

def urlencode(query,quote_plus=False):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        if quote_plus:
            k = quote_plus(str(k))
            gc.collect()
            v = quote_plus(str(v))
            gc.collect()
        else:
            k=str(k)
            gc.collect()
            v=str(v)
            gc.collect()
        l.append(k + '=' + v)
    return '&'.join(l)

