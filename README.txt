==============================
``gs.group.member.invite.csv``
==============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Send invitations to join a group in bulk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-03-19
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product is concerned with the *issuing* of invitations to join an
online group in *bulk* [#base]_, using a CSV file submitted to the *Invite*
form_. Invitations take the form of an email message with a link. The
invitation is responded to using one of the two pages in the
``gs.profile.invite`` module [#profile]_.

Form
====

The ``admin_join_invite_csv.html`` form, in the Group context, takes a CSV
file and invites people to join the group. In the CSV file each row
represents a person, and each column represents a profile attribute.

Overall, the code is hideous, because it is very complex:

* A plain text file has to be parsed, and checked for errors.
* Each row may represent someone who is an existing group member, have an
  existing profile, be new to the system, or the row may be bung. The
  system has to cope for each.
* The entire *Edit profile* infrastructure is needed to add arbitrary
  profile attributes.

The form basically needs to be thrown out and work needs to start again
[#json]_.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.invite.csv
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/

.. [#base] For issuing a single invitation see the base product
          ``gs.group.member.invite.base``:
          <https://source.iopen.net/groupserver/gs.group.member.invite.base>

.. [#profile] See
              <https://source.iopen.net/groupserver/gs.profile.invite>

.. [#json] See `Feature 3494. <https://redmine.iopen.net/issues/3494>`_
..  LocalWords:  CSV html csv
