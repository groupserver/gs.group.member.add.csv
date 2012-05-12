# coding=utf-8
import re, pytz
from string import ascii_letters, digits
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import ASCIILine, Bool, Bytes, Choice, List
from zope.schema import Text, TextLine, URI, ValidationError 
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

class ICsv(Interface):
    """ Schema for processing a CSV file. """
    csv = Bytes(
            title=u"CSV File",
            description=u'The CSV file to be processed.',
      required=True)

