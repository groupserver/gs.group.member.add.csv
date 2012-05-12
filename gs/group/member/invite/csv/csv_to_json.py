# coding=utf-8
''' Implementation of the Edit Image form.
'''
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm

from Products.XWFCore import XWFUtils
from zope.component import createObject
from zope.interface import alsoProvides
from zope.formlib import form
from zope.schema import getFieldsInOrder

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five import BrowserView

from interface import ICsv
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    NotAValidEmailAddress, DisposableEmailAddressNotAllowed, \
    EmailAddressExists


from csv import DictReader

import os

from zif.jsonserver.jsoncomponent import JSONWriter

class CSVJson(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
    
    def __call__(self, *args, **kw):
        data = self.request.form.get('form.csv').read()
        csvResults = DictReader(data.split('\n'), ('email','name'))

        if True:
            self.status = u'Changed %s'
        else:
            self.status = u"No fields changed."
        assert self.status
        assert type(self.status) == unicode

        writer = JSONWriter()
        output = {'fields': csvResults.fieldnames,
                  'rows': []}
        
        for row in csvResults:
            errors = []
            email = row['email']

            emailChecker = NewEmailAddress(title=u'Email')
            emailChecker.context = self.context
            try:
                emailChecker.validate(email)
            except NotAValidEmailAddress:
                errors.append("NotAValidEmailAddress")
            except DisposableEmailAddressNotAllowed:
                errors.append("DisposableEmailAddressNotAllowed")
            except EmailAddressExists:
                errors.append("EmailAddressExists")

            row['errors'] = errors
            output['rows'].append(row)
         
        self.request.RESPONSE.write(writer.write(output))
        self.request.RESPONSE.setHeader('Content-Type','application/json')
    
class CSVJsonForm(PageForm):
    label = u'Process a CSV File into JSON'
    pageTemplateFileName = 'browser/templates/csv_to_json.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(ICsv, render_context=False)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        
        alsoProvides(context, ICsv)

        self.context = context
        self.request = request

    @form.action(label=u'Convert', failure=None)
    def dummy_handler(self, action, data):
        raise NotImplementedError, "This form is dummy, only for testing"

