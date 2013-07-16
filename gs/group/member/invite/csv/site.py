# -*- coding: utf-8 -*-
from zope.component import createObject
from gs.group.member.base import user_member_of_group
from gs.group.member.add.audit import ADD_NEW_USER, ADD_OLD_USER
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.profile.email.base.emailaddress import NewEmailAddress, \
    NotAValidEmailAddress, DisposableEmailAddressNotAllowed, \
    EmailAddressExists
from gs.group.member.invite.base.audit import INVITE_NEW_USER, INVITE_OLD_USER,\
    INVITE_EXISTING_MEMBER
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from create_users_from_csv import CreateUsersInviteForm


class CreateUsersAddSiteForm(CreateUsersInviteForm):
    invite = False

    def __init__(self, site, request):
        super(CreateUsersAddSiteForm, self).__init__(site, request)
        self.site = site
        self.context = site
        del self.group

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
            emailChecker.validate(email)
        except EmailAddressExists, e:
            user = self.acl_users.get_userByEmail(email)
            assert user, 'User for <%s> not found' % email
            userInfo = IGSUserInfo(user)
            auditor, inviter = self.get_auditor_inviter(userInfo)
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
                    inviter.send_notification(self.subject, self.message,
                        inviteId, self.fromAddr, email)
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
