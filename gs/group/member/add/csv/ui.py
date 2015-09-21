# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals, print_function
import sys
if (sys.version_info >= (3, )):
    from urllib.parse import splitquery, quote
else:
    from urllib import splitquery, quote  # lint:ok
from zope.cachedescriptors.property import Lazy
from gs.group.base import GroupPage
from gs.profile.email.base import EmailUser
from gs.group.member.invite.csv.profilelist import ProfileList


class CSVUploadUI(GroupPage):
    def __init__(self, group, request):
        super(CSVUploadUI, self).__init__(group, request)

    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    @Lazy
    def optionalProperties(self):
        retval = [p for p in self.profileList
                  if not self.profileList.properties[p.token].required]
        return retval

    @Lazy
    def requiredProperties(self):
        retval = [p for p in self.profileList
                  if self.profileList.properties[p.token].required]
        return retval

    @Lazy
    def defaultFromEmail(self):
        emailUser = EmailUser(self.context, self.loggedInUserInfo)
        retval = emailUser.get_delivery_addresses()[0]
        return retval

    @Lazy
    def unsupportedEmail(self):
        m = '''Hi,

I would like to add some people to my group, {0}:
  {1}

However, the Add by CSV page does not support my browser. Could you please
add the people for me? I have attached a CSV file below.'''

        msg = m.format(self.groupInfo.name.encode('ascii', 'ignore'),
                       self.groupInfo.url)
        b = quote(msg)
        s = quote('Add by CSV Unsupported')
        retval = 'mailto:{email}?subject={subject}&body={body}'.format(
            email=self.siteInfo.get_support_email(), subject=s, body=b)
        return retval
