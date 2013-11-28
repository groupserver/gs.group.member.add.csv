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
from zope.app.apidoc.interface import getFieldsInOrder
from zope.cachedescriptors.property import Lazy
from zope.interface.common.mapping import IEnumerableMapping
from zope.interface import implements, providedBy
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized, \
    ITitledTokenizedTerm
from zope.schema import *  # FIXME: Delete
from Products.GSProfile import interfaces as profileSchemas
from Products.XWFCore.odict import ODict


class ProfileList(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        if not context:
            raise ValueError('There is no context')
        self.context = context

    @Lazy
    def profileSchemaName(self):
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration'), \
            'No GlobalConfiguration'
        config = site_root.GlobalConfiguration
        ifName = config.getProperty('profileInterface', 'IGSCoreProfile')
        assert hasattr(profileSchemas, ifName), \
            'Interface "%s" not found.' % ifName

        # --=mpj17=-- Sometimes profileInterface is set to ''
        ifName = ifName if ifName else 'IGSCoreProfile'
        retval = '%sAdminJoinCSV' % ifName

        assert retval is not None, 'retval is None'
        assert hasattr(profileSchemas, retval), \
            'Interface "%s" not found.' % retval
        return retval

    @Lazy
    def schema(self):
        return getattr(profileSchemas, self.profileSchemaName)

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        for p in list(self.properties.keys()):
            retval = SimpleTerm(self.properties[p], p, self.properties[p].title)
            assert retval
            assert ITitledTokenizedTerm in providedBy(retval)
            assert retval.value.title == retval.title
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
        for p in self.properties:
            if p == token:
                retval = SimpleTerm(self.properties[p], p,
                                    self.properties[p].title)
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError(token)

    @Lazy
    def properties(self):
        retval = ODict()
        ifs = getFieldsInOrder(self.schema)
        for interface in ifs:
            retval[interface[0]] = interface[1]
        assert isinstance(retval, ODict)
        assert retval
        return retval
