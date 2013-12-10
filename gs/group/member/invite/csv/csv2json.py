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
from StringIO import StringIO
from zope.cachedescriptors.property import Lazy
from zope.formlib import form as formlib
from gs.content.form.api.json import GroupEndpoint
from gs.content.form import multi_check_box_widget
from .interface import ICsv
from .unicodereader import UnicodeDictReader


class CSV2JSON(GroupEndpoint):
    label = 'POST CSV data to this URL to parse it, and transform it into ' \
            'a JSON object.'

    def __init__(self, group, request):
        super(CSV2JSON, self).__init__(group, request)

    @Lazy
    def form_fields(self):
        retval = formlib.Fields(ICsv, render_context=False)
        retval['columns'].custom_widget = multi_check_box_widget
        assert retval
        return retval

    @formlib.action(label='Submit', prefix='', failure='process_failure')
    def process_success(self, action, data):
        cols = data['columns']
        csv = StringIO(data['csv'])
        # TODO: Delivery?

        reader = UnicodeDictReader(csv, cols)
        try:
            next(reader)  # Skip the first row (the header)
        except UnicodeDecodeError as e:
            m = {'status': -2,
                'message': ['Could not read the file. Please check that you '
                            'selected the correct CSV file.',
                            str(e)]}
            retval = to_json(m)
        else:
            profiles = []
            rowCount = 0
            for row in reader:
                rowCount += 1
                if len(row) > len(cols):
                    msg = 'Row {0} had {1} columns, rather than {2}. Please ' \
                            'check the file and the columns.'
                    # Name hack.
                    profiles = {'status': -3,
                                'message': [msg.format(rowCount, len(row),
                                                        len(cols))]}
                    # --=mpj17=-- I think this is the first time I have used
                    # break in actual code. Wow.
                    break
                profiles.append(row)
            retval = to_json(profiles)
        return retval

    def process_failure(self, action, data, errors):
        retval = self.build_error_response(action, data, errors)
        return retval
