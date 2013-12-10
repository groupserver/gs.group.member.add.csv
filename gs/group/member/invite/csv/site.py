# -*- coding: utf-8 -*-
from columns import Columns
from create_users_from_csv import CreateUsersInviteForm
from site_processor import CSVSiteProcessor


class CreateUsersAddSiteForm(CreateUsersInviteForm):
    invite = False

    def __init__(self, site, request):
        super(CreateUsersAddSiteForm, self).__init__(site, request)
        self.site = site
        self.context = site
        del self.group

    def process_form(self):
        # FIXME: A hideous hack: only one (1, i) line is different from super()
        form = self.context.REQUEST.form
        result = {}
        result['form'] = form

        if 'submitted' in form:
            result['message'] = u''
            result['error'] = False

            # Processing the CSV is done in three stages.
            #   1. Process the columns.
            columnProcessor = Columns(self.context, form)
            r = columnProcessor.process()
            result['message'] = u'\n'.join((result['message'], r['message']))
            result['error'] = result['error'] if result['error'] else r['error']
            columns = r['columns']

            # FIXME: vvv This is the only line that is different vvvv
            processor = CSVSiteProcessor(self.context, self.request, form,
                                        columns, self.fromAddr,
                                        self.profileSchema, self.profileFields)

            #   2. Parse the file.
            if not result['error']:
                r = processor.process()
                result['message'] = u'\n'.join((result['message'],
                                                r['message']))
                result['error'] = result['error'] or r['error']
                csvResults = r['csvResults']
            #   3. Interpret the data.
            if not result['error']:
                try:
                    r = processor.process_csv_results(csvResults,
                                                        form['delivery'])
                except UnicodeDecodeError, ude:
                    result['error'] = True
                    m = u'<p>Error reading the CSV file (did you select the '\
                        u'correct file?): <span class="muted">{0}</p></p>'
                    result['message'] = m.format(ude)
                else:
                    m = u'\n'.join((result['message'], r['message']))
                    result['message'] = m
                    result['error'] = result['error'] or r['error']

            assert 'error' in result
            assert type(result['error']) == bool
            assert 'message' in result
            assert type(result['message']) == unicode

        assert type(result) == dict
        assert 'form' in result
        assert type(result['form']) == dict

        contentType = 'text/html; charset=UTF-8'
        self.request.response.setHeader('Content-Type', contentType)
        return result
