# -*- coding: utf-8 -*-
# <http://docs.python.org/2.7/library/csv.html#csv.DictReader>
import codecs
from csv import DictReader, excel


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, cols, dialect=excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = DictReader(f, cols, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        retval = dict([(to_unicode_or_bust(k), to_unicode_or_bust(v))
                        for k, v in row.items()])
        return retval

    def __iter__(self):
        return self


def to_unicode_or_bust(obj, encoding='utf-8'):
    'http://farmdev.com/talks/unicode/'
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj
