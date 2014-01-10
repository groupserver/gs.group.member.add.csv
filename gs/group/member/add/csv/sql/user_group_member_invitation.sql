SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE user_group_member_invitation (
    INVITATION_ID        TEXT                        PRIMARY KEY,
    USER_ID              TEXT                        NOT NULL,
    INVITING_USER_ID     TEXT                        NOT NULL,
    SITE_ID              TEXT                        NOT NULL,
    GROUP_ID             TEXT                        NOT NULL,
    INVITATION_DATE      TIMESTAMP WITH TIME ZONE    NOT NULL,
    INITIAL_INVITE       BOOL                        DEFAULT FALSE,
    RESPONSE_DATE        TIMESTAMP WITH TIME ZONE    DEFAULT NULL,
    ACCEPTED             BOOL                        DEFAULT FALSE,
    WITHDRAWN_DATE       TIMESTAMP WITH TIME ZONE    DEFAULT NULL,
    WITHDRAWING_USER_ID  TIMESTAMP WITH TIME ZONE    DEFAULT NULL
);
--=mpj17=-- There is no foreign key for user_id, yet

-- INVITATION_DATE is the date the user was invited to join the group
-- INITIAL_INVITE is TRUE if it is the invitation to the *system*, rather
--    than an invitation just to a group
-- RESPONSE_DATE is the date the user responded to the invitation. If the
--    user has not responded to the invitation, it is NULL.
-- ACCEPTED is TRUE if the user accepted the invitation when he or she
--    responded; FALSE otherwise.
-- WITHDRAWN_DATE is the date the invitation was withdrawn by an 
--    administrator. If the invitation was not withdrawn it will be NULL.
-- WITHDRAWING_USER_ID is the ID of the administrator who withdrew the
--    invitation.

