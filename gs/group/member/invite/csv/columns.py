# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from profilelist import ProfileList


class Columns(object):

    def __init__(self, context, form):
        if not context:
            m = u'Context not supplied'
            raise ValueError(m)
        self.context = context

        if type(form) != dict:
            m = u'The form is not a dictionary'
            raise TypeError(m)
        self.form = form

    @Lazy
    def profileList(self):
        retval = ProfileList(self.context)
        return retval

    def process(self):
        '''Process the columns specified by the user.

        DESCRIPTION
          The administrator can create a CSV with the columns in any
          order that he or she likes. However, the admin must specify
          the columns seperately so we know what is entered. The job
          of this method is to parse the column spec.

        ARGUMENTS
          form:     The form that contains the column specifications.

        SIDE EFFECTS
          None.

        RETURNS
          A dictionary containing the following keys.
            error     bool    True if an error was encounter.
            message   str     A feedback message.
            columns   list    The columns the user specified. The list
                              values are column IDs as strings.
            form      dict    The form that was passed as an argument.
        '''
        message = u''
        error = False

        colDict = {}
        for key in self.form:
            if 'column' in key and self.form[key] != 'nothing':
                foo, col = key.split('column')
                i = ord(col) - 65
                colDict[i] = self.form[key]
        columns = [colDict[i] for i in range(0, len(colDict))]

        unspecified = self.get_unspecified_columns(columns)
        if unspecified:
            error = True
            colPlural = len(unspecified) > 1 and 'columns have' \
              or 'column has'
            colM = '\n'.join(['<li>%s</li>' % c.title for c in unspecified])
            m = u'<p>The required %s not been specified:</p>\n<ul>%s</ul>' %\
              (colPlural, colM)
            message = u'%s\n%s' % (message, m)

        result = {'error': error,
                  'message': message,
                  'columns': columns,
                  'form': self.form}
        assert 'error' in result
        assert type(result['error']) == bool
        assert 'message' in result
        assert type(result['message']) == unicode
        assert 'columns' in result
        assert type(result['columns']) == list
        assert len(result['columns']) >= 2
        assert 'form' in result
        assert type(result['form']) == dict
        return result

    def get_unspecified_columns(self, columns):
        '''Get the unspecified required columns'''
        unspecified = []
        for requiredColumn in self.requiredColumns:
            if requiredColumn.token not in columns:
                unspecified.append(requiredColumn)
        return unspecified

    @Lazy
    def requiredColumns(self):
        retval = [p for p in self.profileList if p.value.required]
        return retval
