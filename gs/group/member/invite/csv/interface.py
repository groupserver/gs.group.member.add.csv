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
from __future__ import absolute_import
from zope.cachedescriptors.property import Lazy
from zope.interface.interface import Interface
from zope.schema import Bytes, List, ValidationError
from .profilelist import ProfileList


class RequiredAttributeMissingError(ValidationError):

    def __init__(self, value):
        super(RequiredAttributeMissingError, self).__init__(value)
        self.value = value

    def __unicode__(self):
        m = u'The required attribute {0} is missing'
        retval = m.format(self.value)
        return retval

    def __str__(self):
        retval = unicode(self).encode('ascii', 'ignore')
        return retval

    def __doc__(self):
        return str(self)


class ProfilesList(List):

    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    def constraint(self, value):
        required = [attr.id for attr in self.profileList if attr.required]
        for attr in required:
            if attr not in value:
                raise RequiredAttributeMissingError(attr)
        return True


class ICsv(Interface):
    """ Schema for processing a CSV file. """
    csv = Bytes(title=u"CSV File",
            description=u'The CSV file to be processed.',
            required=True)

    columns = List(title=u'Columns',
                description=u'The columns in the CSV.',
                required=True)
