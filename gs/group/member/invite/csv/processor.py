# -*- coding: utf-8 -*-
from csv import DictReader, Error as CSVError
from zope.component import createObject
from zope.formlib import form as formlib
from gs.content.form.utils import enforce_schema
from gs.group.member.base import user_member_of_group
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.group.member.invite.base.audit import Auditor, INVITE_NEW_USER, \
                                      INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from gs.group.member.invite.base.inviter import Inviter
from gs.group.member.add.audit import ADD_NEW_USER, ADD_OLD_USER, \
    Auditor as AddAuditor
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    NotAValidEmailAddress, DisposableEmailAddressNotAllowed, \
    EmailAddressExists
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSProfile.utils import create_user_from_email
from Products.GSProfile.interfaceCoreProfile import deliveryVocab


class CSVProcessor(object):

    def __init__(self, form, columns):
        if type(form) != dict:
            m = u'The form is not a dictionary'
            raise TypeError(m)

        self.form = form
        self.columns = columns

    def process(self):
        '''Process the CSV file specified by the user.

        DESCRIPTION
          Parse the CSV file that is supplied as part of the `form`. The
          parser turns each row into a dictionary, which has `columns`
          as the keys.

        ARGUMENTS
          form:     The form that contains the CSV file.
          columns:  The columns specification, as generated by
                    "process_columns".

        SIDE EFFECTS
          None.

        RETURNS
          A dictionary containing the following keys.

            Key         Type      Note
            ==========  ========  =======================================
            error       bool      True if an error was encounter.
            message     str       A feedback message.
            csvResults  instance  An instance of a DictReader
            form        dict      The form that was passed as an argument.
        '''

        message = u''
        error = False
        if 'csvfile' in self.form:
            csvfile = self.form.get('csvfile')
            csvResults = DictReader(csvfile, self.columns)
        else:
            message = u'<p>There was no CSV file specified. Please specify a '\
                  u'CSV file</p>'
            error = True
            csvfile = None
            csvResults = None
        result = {'error': error,
                  'message': message,
                  'csvResults': csvResults,
                  'form': self.form}
        assert 'error' in result
        assert type(result['error']) == bool
        assert 'message' in result
        assert type(result['message']) == unicode
        assert 'csvResults' in result
        assert isinstance(result['csvResults'], DictReader)
        assert 'form' in result
        assert type(result['form']) == dict
        return result

    def process_csv_results(self, csvResults, delivery):
        '''Process the CSV results, creating users and adding them to
           the group as necessary.

        ARGUMENTS
          csvResults: The CSV results, as generated by the `processor` method.
          delivery:   The email delivery settings for the new group
                      members.

        SIDE EFFECTS
          For each user in the CSV results, either
            * A new user is created if the user's email address is not
              registered with the system, or
            * The user is added to the site and group, if the user is not
              already a member.
          The side-effect is actually created by "process_row", which is
          called by this method.

        RETURNS
          A dictionary containing the following keys.
            error       bool      True if an error was encounter.
            message     str       A feedback message.
        '''
        assert isinstance(csvResults, DictReader)

        errorMessage = u'<ul>\n'
        errorCount = 0
        error = False
        newUserCount = 0
        newUserMessage = u'<ul>\n'
        existingUserCount = 0
        existingUserMessage = u'<ul>\n'
        skippedUserCount = 0
        skippedUserMessage = u'<ul>\n'
        rowCount = 0
        try:
            csvResults.next()  # Skip the first row (the header)
        except CSVError as csvError:
            m = u'{0}\n<li><strong>Error reading the CSV header:</strong> '\
                u'{1}</li>'
            result = {'error': True,
                      'message': m.format(errorMessage, unicode(csvError))}
            # Sorry, Dijkstra
            return result

        # Map the data into the correctly named columns.
        try:
            for row in csvResults:
                try:
                    r = self.process_row(row, delivery)
                    error = error or r['error']

                    if r['error']:
                        errorCount = errorCount + 1
                        errorMessage = u'%s\n<li>%s</li>' %\
                          (errorMessage, r['message'])
                    elif r['new'] == 1:
                        existingUserCount = existingUserCount + 1
                        existingUserMessage = u'%s\n<li>%s</li>' %\
                          (existingUserMessage, r['message'])
                    elif r['new'] == 2:
                        newUserCount = newUserCount + 1
                        newUserMessage = u'%s\n<li>%s</li>' %\
                          (newUserMessage, r['message'])
                    elif r['new'] == 3:
                        skippedUserCount = skippedUserCount + 1
                        skippedUserMessage = u'%s\n<li>%s</li>' %\
                          (skippedUserMessage, r['message'])
                    else:
                        assert False, 'Unexpected return value from process_'\
                            'row: %d' % r['new']
                except Exception, e:
                    error = True
                    errorCount = errorCount + 1
                    m = u'{0}\n<li><strong>Unexpected Error:</strong> {1}</li>'
                    errorMessage = m.format(errorMessage, unicode(e))
                rowCount = rowCount + 1

                assert (existingUserCount + newUserCount + errorCount +
                  skippedUserCount) == rowCount,\
                  u'Discrepancy between counts: %d + %d + %d + %d != %d' %\
                    (existingUserCount, newUserCount, errorCount,
                     skippedUserCount, rowCount)

        except CSVError as csvError:
            error = True
            errorCount = errorCount + 1
            m = u'{0}\n<li><strong>Error reading the CSV file:</strong> '\
                u'{1}</li>'
            errorMessage = m.format(errorMessage, unicode(csvError))

        message = u'<p>%d rows were processed.</p>\n<ul>\n' %\
          (rowCount + 1)
        message = u'%s<li>The first row was treated as a header, and '\
          u'ignored.</li>\n' % message

        newUserMessage = u'%s</ul>\n' % newUserMessage
        if newUserCount > 0:
            wasWere = newUserCount == 1 and 'was' or 'were'
            userUsers = newUserCount == 1 and 'profile' or 'profiles'
            personPeople = newUserCount == 1 and 'person' or 'people'
            message = u'%s<li id="newUserInfo" class="disclosureWidget">'\
              u'<a href="#" class="disclosureButton"><strong>%d new '\
              u'%s</strong> %s created, and the %s %s invited to join '\
              u'%s.</a>\n<div class="disclosureShowHide" '\
              u'style="display:none;">%s</div></li>' % (message, newUserCount,
                userUsers, wasWere, personPeople, wasWere, self.groupInfo.name,
                newUserMessage)

        existingUserMessage = u'%s</ul>\n' % existingUserMessage
        if existingUserCount > 0:
            userUsers = existingUserCount == 1 and 'person' or 'people'
            wasWere = existingUserCount == 1 and 'was' or 'were'
            message = u'%s<li id="existingUserInfo"'\
              u'class="disclosureWidget">'\
              u'<a href="#" class="disclosureButton">%d %s that '\
              u'<strong>already had a profile</strong> %s invited to '\
              u'join to %s.</a>\n'\
              u'<div class="disclosureShowHide" style="display:none;">'\
              u'%s</div></li>' % (message, existingUserCount, userUsers,
                wasWere, self.groupInfo.name, existingUserMessage)

        skippedUserMessage = u'%s</ul>\n' % skippedUserMessage
        if skippedUserCount > 0:
            userUsers = skippedUserCount == 1 and 'member' or 'members'
            wasWere = skippedUserCount == 1 and 'was' or 'were'
            message = u'%s<li id="skippedUserInfo"'\
              u'class="disclosureWidget">'\
              u'<a href="#" class="disclosureButton"><strong>%d existing '\
              u'%s of %s %s skipped.</strong></a>\n'\
              u'<div class="disclosureShowHide" style="display:none;">'\
              u'%s</div></li>' % (message, skippedUserCount, userUsers,
                self.groupInfo.name, wasWere, skippedUserMessage)

        errorMessage = u'%s</ul>\n' % errorMessage
        if error:
            wasWere = errorCount == 1 and 'was' or 'were'
            errorErrors = errorCount == 1 and 'error' or 'errors'
            message = u'%s</ul><p>There %s %d %s:</p>\n' % \
              (message, wasWere, errorCount, errorErrors)
            message = u'%s%s\n' % (message, errorMessage)

        result = {'error': error,
                  'message': message}

        assert 'error' in result
        assert type(result['error']) == bool
        assert 'message' in result
        assert type(result['message']) == unicode

        return result

    def process_row(self, row, delivery):
        '''Process a row from the CSV file

        ARGUMENTS
          row        dict    The fields representing a row in the
                             CSV file. The column identifiers (alias
                             profile attribute identifiers) form
                             the keys.
          delivery   str     The message delivery settings for the new
                             group members

        SIDE EFFECTS
            * A new user is created if the user's email address
              "fields['email']" is not registered with the system, or
            * The user is added to the site and group, if the user is not
              already a member.

        RETURNS
          A dictionary containing the following keys.
            error       bool      True if an error was encounter.
            message     str       A feedback message.
            new         int       1 if an existing user was added to the
                                    group
                                  2 if a new user was created and added
                                  3 if the user was skipped as he or she
                                    is already a group member
                                  0 on error.
            user        instance  An instance of the CustomUser class.
        '''
        assert type(row) == dict
        assert 'toAddr' in row.keys(), '"toAddr" is not in row.keys()'
        assert row['toAddr']

        user = None
        new = 0

        email = row['toAddr'].strip()

        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context  # --=mpj17=-- Legit?
        try:
            emailChecker.validate(email)
        except EmailAddressExists, e:
            user = self.acl_users.get_userByEmail(email)
            assert user, u'User for <%s> not found' % email
            userInfo = IGSUserInfo(user)
            auditor, inviter = self.get_auditor_inviter(userInfo)
            if user_member_of_group(user, self.groupInfo):
                new = 3
                auditor.info(INVITE_EXISTING_MEMBER, email)
                m = u'Skipped existing group member %s' % \
                    userInfo_to_anchor(userInfo)
            else:
                new = 1
                if self.invite:
                    inviteId = inviter.create_invitation(row, False)
                    auditor.info(INVITE_OLD_USER, email)
                    inviter.send_notification(self.subject, self.message,
                        inviteId, self.fromAddr, email)
                    # transaction.commit()
                else:
                    # almighty hack
                    # get the user object in the context of the group and site
                    userInfo = createObject('groupserver.UserFromId',
                                  self.groupInfo.groupObj,
                                  user.id)
                    auditor.info(ADD_OLD_USER, email)
                    joininguser = IGSJoiningUser(userInfo)
                    joininguser.join(self.groupInfo)
                    # transaction.commit()
                self.set_delivery_for_user(userInfo, delivery)
                m = u'%s has an existing profile' % userInfo_to_anchor(userInfo)
            error = False
        except DisposableEmailAddressNotAllowed, e:
            error = True
            m = self.error_msg(email, unicode(e))
        except NotAValidEmailAddress, e:
            error = True
            m = self.error_msg(email, unicode(e))
        else:
            userInfo = self.create_user(row)
            user = userInfo.user
            new = 2
            auditor, inviter = self.get_auditor_inviter(userInfo)
            if self.invite:
                inviteId = inviter.create_invitation(row, True)
                auditor.info(INVITE_NEW_USER, email)
                # transaction.commit()

                inviter.send_notification(self.subject, self.message,
                    inviteId, self.fromAddr, email)
            else:
                # almight hack
                # get the user object in the context of the group and site
                userInfo = createObject('groupserver.UserFromId',
                                  self.groupInfo.groupObj,
                                  user.id)
                # force verify
                vid = '%s-%s-verified' % (email, self.adminInfo.id)
                evu = createObject('groupserver.EmailVerificationUserFromEmail',
                                    self.context, email)
                evu.add_verification_id(vid)
                evu.verify_email(vid)

                auditor.info(ADD_NEW_USER, email)
                joininguser = IGSJoiningUser(userInfo)

                joininguser.join(self.groupInfo)

            self.set_delivery_for_user(userInfo, delivery)
            error = False
            m = u'Created a profile for %s' % userInfo_to_anchor(userInfo)

        result = {'error': error,
                  'message': m,
                  'user': user,
                  'new': new}
        assert result
        assert type(result) == dict
        assert 'error' in result
        assert type(result['error']) == bool
        assert 'message' in result
        assert type(result['message']) == unicode
        assert 'user' in result
        # If an email address is invalid or disposable, user==None
        #assert isinstance(result['user'], CustomUser)
        assert 'new' in result
        assert type(result['new']) == int
        assert result['new'] in range(0, 5), '%d not in range' % result['new']

        return result

    def create_user(self, fields):
        assert type(fields) == dict
        assert 'toAddr' in fields
        assert fields['toAddr']

        email = fields['toAddr'].strip()

        user = create_user_from_email(self.context, email)
        userInfo = IGSUserInfo(user)
        enforce_schema(userInfo.user, self.profileSchema)
        formlib.applyChanges(user, self.profileFields, fields)
        return userInfo

    def error_msg(self, email, msg):
        return\
          u'Did not create a profile for the email address '\
          u'<code class="email">%s</code>. %s' % (email, msg)

    def set_delivery_for_user(self, userInfo, delivery):
        '''Set the message delivery setting for the user

        ARGUMENTS
            userInfo    A UserInfo instance.
            delivery    The delivery settings as a string.

        SIDE EFFECTS
            Sets the delivery setting for the user in the group

        RETURNS
            None.
        '''
        assert not(userInfo.anonymous)
        assert delivery in deliveryVocab

        if delivery == 'email':
            # --=mpj17=-- The default is one email per post
            pass
        elif delivery == 'digest':
            userInfo.user.set_enableDigestByKey(self.groupInfo.id)
        elif delivery == 'web':
            userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)

    def get_auditor_inviter(self, userInfo):
        if self.invite:
            inviter = Inviter(self.context, self.request, userInfo,
                              self.adminInfo, self.siteInfo,
                              self.groupInfo)
        else:
            inviter = None

        if self.invite:
            auditor = Auditor(self.siteInfo, self.groupInfo,
                              self.adminInfo, userInfo)
        else:
            auditor = AddAuditor(self.siteInfo, self.groupInfo,
                                    self.adminInfo, userInfo)

        return (auditor, inviter)
