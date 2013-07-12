# coding=utf-8
from zope.interface.interface import Interface
from zope.schema import Bytes


class ICsv(Interface):
    """ Schema for processing a CSV file. """
    csv = Bytes(
            title=u"CSV File",
            description=u'The CSV file to be processed.',
      required=True)
