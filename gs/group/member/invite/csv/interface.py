# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from zope.interface.interface import Interface
from zope.schema import Choice, List, ValidationError  # Bytes,


class RequiredAttributeMissingError(ValidationError):

    def __init__(self, value):
        super(RequiredAttributeMissingError, self).__init__(value)
        self.value = value

    def __unicode__(self):
        m = 'The required attribute {0} is missing'
        retval = m.format(self.value)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    def __doc__(self):
        return str(self)


class ICsv(Interface):
    """ Schema for processing a CSV file. """
    #csv = Bytes(title="CSV File",
            #description='The CSV file to be processed.',
            #required=True)

    columns = List(title='Columns',
                description='The columns in the CSV.',
                value_type=Choice(title='Profile attribute',
                                    vocabulary='ProfileAttributes'),
                unique=True,
                required=True)

    #columns = Text(title='c', required=False)
