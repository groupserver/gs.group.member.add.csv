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
from zope.app.apidoc.interface import getFieldsInOrder
from zope.cachedescriptors.property import Lazy
from zope.interface.common.mapping import IEnumerableMapping
from zope.schema.vocabulary import SimpleTerm
from zope.schema import *  # FIXME: Delete
from gs.profile.email.base.emailaddress import EmailAddress
from Products.GSProfile import interfaces as profileSchemas
from Products.XWFCore.odict import ODict
from .error import GlobalConfigError, ProfileNotFound


class ProfileList(object):
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        if not context:
            raise ValueError('There is no context')
        self.context = context

    @Lazy
    def properties(self):
        retval = ODict()
        retval['email'] = EmailAddress(title='Email',
                            description='The email address of the new member')
        ifs = getFieldsInOrder(self.schema)
        for interface in ifs:
            key = unicode(interface[0])
            retval[key] = interface[1]
        assert isinstance(retval, ODict)
        assert retval
        return retval

    def property_to_token(self, p):
        retval = SimpleTerm(p, p, self.properties[p].title)
        return retval

    @Lazy
    def profileSchemaName(self):
        site_root = self.context.site_root()
        if not site_root:
            raise GlobalConfigError('Global configuration not found')
        config = site_root.GlobalConfiguration
        ifName = config.getProperty('profileInterface', 'IGSCoreProfile')
        if not hasattr(profileSchemas, ifName):
            raise ProfileNotFound('Interface "{0}" not found.'.format(ifName))

        # --=mpj17=-- Sometimes profileInterface is set to ''
        retval = ifName if ifName else 'IGSCoreProfile'
        if retval is None:
            raise TypeError('retval is None')
        if not hasattr(profileSchemas, retval):
            raise ValueError('Interface "{0}" not found.'.format(retval))
        return retval

    @Lazy
    def schema(self):
        return getattr(profileSchemas, self.profileSchemaName)

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        for p in list(self.properties.keys()):
            retval = self.property_to_token(p)
            assert retval
            yield retval

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.properties)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = value in self.properties
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for p in self.properties.keys():
            if p == token:
                retval = self.property_to_token(p)
                assert retval
                return retval
        raise LookupError(token)
