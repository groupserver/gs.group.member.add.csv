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
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from .interface import ICsv
from .profilelist import ProfileList
from .unicodereader import UnicodeDictReader


class CSV2JSON(GroupEndpoint):

    def __init__(self, group, request):
        super(CSV2JSON, self).__init__(group, request)

    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    @Lazy
    def requiredColumns(self):
        retval = [p for p in self.profileList if p.value.required]
        return retval

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(ICsv, render_context=False)
        assert retval
        return retval

    @formlib.action(label=u'Submit', prefix='', failure='process_failure')
    def process_success(self, action, data):
        csv = data['csv']
        cols = data['columns']
        # TODO: check the required columns are present.
        reader = UnicodeDictReader(csv, cols)
        print reader

    def process_failure(self, action, data, errors):
        retval = self.build_error_response(action, data, errors)
        return retval
