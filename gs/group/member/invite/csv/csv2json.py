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
from json import dumps as to_json
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from gs.content.form import multi_check_box_widget
from .interface import ICsv
# from .unicodereader import UnicodeDictReader


class CSV2JSON(GroupEndpoint):
    label = 'POST CSV data to this URL to parse it, and transform it into ' \
            'a JSON object.'

    def __init__(self, group, request):
        super(CSV2JSON, self).__init__(group, request)
        print request.form

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(ICsv, render_context=False)
        retval['columns'].custom_widget = multi_check_box_widget
        assert retval
        return retval

    @formlib.action(label='Submit', prefix='', failure='process_failure')
    def process_success(self, action, data):
        #csv = data['csv']
        cols = data['columns']
        # TODO: Delivery?

        #reader = UnicodeDictReader(csv, cols)
        #reader.next()  # Skip the first row (the header)
        #profiles = []
        #for row in reader:
        #    profiles.append(row)
        #retval = to_json(profiles)
        retval = to_json(cols)
        return retval

    def process_failure(self, action, data, errors):
        retval = self.build_error_response(action, data, errors)
        return retval
