# -*- coding: utf-8 -*-
import re

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'_'):
    """Generates slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return delim.join(result)
