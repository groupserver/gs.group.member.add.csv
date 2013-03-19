# -*- coding: utf-8 -*-
from zope.app.apidoc.interface import getFieldsInOrder
from zope.interface.common.mapping import IEnumerableMapping
from zope.interface import implements, providedBy
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized, \
    ITitledTokenizedTerm
from zope.schema import *
from Products.XWFCore.odict import ODict


class ProfileList(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.__properties = ODict()
        self.__profileInterfaceName = None

    @property
    def profileSchemaName(self):
        if self.__profileInterfaceName is None:
            site_root = self.context.site_root()
            assert hasattr(site_root, 'GlobalConfiguration')
            config = site_root.GlobalConfiguration
            ifName = config.getProperty('profileInterface', 'IGSCoreProfile')
            # --=mpj17=-- Sometimes profileInterface is set to ''
            ifName = (ifName and ifName) or 'IGSCoreProfile'
            self.__profileInterfaceName = '%sAdminJoinCSV' % ifName
            assert self.__profileInterfaceName is not None
            assert hasattr(profileSchemas, ifName), \
                'Interface "%s" not found.' % ifName
            assert hasattr(profileSchemas, self.__profileInterfaceName), \
                'Interface "%s" not found.' % self.__profileInterfaceName
        return self.__profileInterfaceName

    @property
    def schema(self):
        return getattr(profileSchemas, self.profileSchemaName)

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm(self.properties[p], p, self.properties[p].title)
                  for p in self.properties.keys()]
        for term in retval:
            assert term
            assert ITitledTokenizedTerm in providedBy(term)
            assert term.value.title == term.title
        return iter(retval)

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

    @property
    def properties(self):
        if len(self.__properties) == 0:
            assert self.context
            ifs = getFieldsInOrder(self.schema)
            for interface in ifs:
                self.__properties[interface[0]] = interface[1]
        retval = self.__properties
        assert isinstance(retval, ODict)
        assert retval
        return retval
