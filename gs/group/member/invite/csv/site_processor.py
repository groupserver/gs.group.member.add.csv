# -*- coding: utf-8 -*-
from zope.component import createObject
from gs.group.member.base import user_member_of_group
from gs.group.member.add.audit import ADD_NEW_USER, ADD_OLD_USER, \
    Auditor as AddAuditor
from gs.group.member.invite.base.audit import Auditor, INVITE_NEW_USER, \
                                      INVITE_OLD_USER, INVITE_EXISTING_MEMBER
from gs.group.member.invite.base.inviter import Inviter
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    NotAValidEmailAddress, DisposableEmailAddressNotAllowed, \
    EmailAddressExists
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from processor import CSVProcessor


class CSVSiteProcessor(CSVProcessor):

    def __init__(self, context, request, form, columns, fromAddr, profileSchema,
                    profileFields):
        # TODO: Remove the HACK with the subject and message
        super(CSVSiteProcessor, self).__init__(context, request, form, columns,
                                                u'sub', u'msg',  # FIXME: Hack
                                                fromAddr, profileSchema,
                                                profileFields)

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
        assert 'toAddr' in row.keys()
        assert row['toAddr']

        user = None
        new = 0

        email = row['toAddr'].strip()
        groupId = row['groupId'].strip()
        groupInfo = createObject('groupserver.GroupInfo', self.context, groupId)
        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context  # --=mpj17=-- Legit?
        try:
            asciiEmail = email.encode('ascii', 'ignore')
            emailChecker.validate(asciiEmail)  # email addrs must be ASCII
        except EmailAddressExists, e:
            user = self.acl_users.get_userByEmail(email)
            assert user, 'User for <%s> not found' % email
            userInfo = IGSUserInfo(user)
            # FIXME: vvv This is also different vvvv
            auditor, inviter = self.get_auditor_inviter(userInfo, groupInfo)
            if user_member_of_group(user, groupInfo):
                new = 3
                auditor.info(INVITE_EXISTING_MEMBER, email)
                m = u'Skipped existing group member %s' % \
                    userInfo_to_anchor(userInfo)
            else:
                new = 1
                if self.invite:
                    inviteId = inviter.create_invitation(row, False)
                    auditor.info(INVITE_OLD_USER, email)
                    subject = self.get_subject(groupInfo)
                    message = self.get_message(groupInfo)
                    inviter.send_notification(subject, message, inviteId,
                                                self.fromAddr, email)
                    # transaction.commit()
                else:
                    # almighty hack
                    # get the user object in the context of the group and site
                    userInfo = createObject('groupserver.UserFromId',
                                  groupInfo.groupObj,
                                  user.id)
                    auditor.info(ADD_OLD_USER, email)
                    joininguser = IGSJoiningUser(userInfo)
                    joininguser.join(groupInfo)
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
            auditor, inviter = self.get_auditor_inviter(userInfo, groupInfo)
            if self.invite:
                inviteId = inviter.create_invitation(row, True)
                auditor.info(INVITE_NEW_USER, email)
                # transaction.commit()

                inviter.send_notification(self.subject, self.message,
                    inviteId, self.fromAddr, email)
            else:
                # almighty hack
                # get the user object in the context of the group and site
                userInfo = createObject('groupserver.UserFromId',
                                  groupInfo.groupObj,
                                  user.id)
                # force verify
                vid = '%s-%s-verified' % (email, self.adminInfo.id)
                evu = createObject('groupserver.EmailVerificationUserFromEmail',
                                    self.context, email)
                evu.add_verification_id(vid)
                evu.verify_email(vid)

                auditor.info(ADD_NEW_USER, email)
                joininguser = IGSJoiningUser(userInfo)

                joininguser.join(groupInfo)

            self.set_delivery_for_user(userInfo, delivery)
            error = False
            m = u'Created a profile for %s' % userInfo_to_anchor(userInfo)

        result = {'error': error, 'message': m, 'user': user, 'new': new}
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

    def get_subject(self, groupInfo):
        m = u'Invitation to join {groupInfo.name}'
        retval = m.format(groupInfo=groupInfo)
        return retval

    def get_message(self, groupInfo):
        m = m = u'''Hi there!

Please accept this invitation to join {groupinfo.name}. I have set
everything up for you, so you can start participating in the group as soon as
you follow the link below and accept this invitation.'''
        retval = m.format(groupInfo=groupInfo)
        return retval

    def get_auditor_inviter(self, userInfo, groupInfo):
        if self.invite:
            inviter = Inviter(self.context, self.request, userInfo,
                              self.adminInfo, self.siteInfo,
                              groupInfo)
        else:
            inviter = None

        if self.invite:
            auditor = Auditor(self.siteInfo, groupInfo,
                              self.adminInfo, userInfo)
        else:
            auditor = AddAuditor(self.siteInfo, groupInfo,
                                    self.adminInfo, userInfo)

        return (auditor, inviter)
