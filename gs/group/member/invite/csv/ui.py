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
from zope.cachedescriptors.property import Lazy
from gs.group.base import GroupPage
from .profilelist import ProfileList


class CSVUploadUI(GroupPage):
    def __init__(self, group, request):
        super(CSVUploadUI, self).__init__(group, request)

    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    @Lazy
    def optionalProperties(self):
        retval = [p for p in self.profileList if not p.value.required]
        return retval
