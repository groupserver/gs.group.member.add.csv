# coding=utf-8
from csv import DictReader
from zope.formlib import form
from zope.interface import alsoProvides
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base import GroupForm, GroupPage
from interface import ICsv
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    NotAValidEmailAddress, DisposableEmailAddressNotAllowed, \
    EmailAddressExists
from zif.jsonserver.jsoncomponent import JSONWriter


class CSVJson(GroupPage):
    def __init__(self, context, request):
        super(CSVJson, self).__init__(context, request)

    def __call__(self, *args, **kw):
        data = self.request.form.get('form.csv').read()
        csvResults = DictReader(data.split('\n'), ('email', 'name'))

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
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')


class CSVJsonForm(GroupForm):
    label = u'Process a CSV File into JSON'
    pageTemplateFileName = 'browser/templates/csv_to_json.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(ICsv, render_context=False)

    def __init__(self, group, request):
        super(CSVJsonForm, self).__init__(group, request)
        alsoProvides(group, ICsv)

    @form.action(label=u'Convert', failure=None)
    def dummy_handler(self, action, data):
        raise NotImplementedError("This form is dummy, only for testing")
