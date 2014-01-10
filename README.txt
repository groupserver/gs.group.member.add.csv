===========================
``gs.group.member.add.csv``
===========================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add people to join a group in bulk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-01-10
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product is concerned with the adding people to an
online group in *bulk* [#base]_, using a CSV file submitted to a
form_. Most of the page is powered by JavaScript_.

Form
====

The ``admin_add_csv.html`` form, in the Group context, takes a CSV file
and add each person in the file (one per row) to join the group. The
work is done in two main steps — parsing and adding — which is
controlled by JavaScript_.

The **parsing** is done by a product provided by the
``gs.group.member.invite.base`` product [#invite]_.

The **adding** is actually carried out by ``gs.group.member.add.json``
[#json]_.

JavaScript
==========

The JavaScript is supplied by the ``gs.group.member.invite.csv`` product
[#invite]_. The script is pointed at the JSON-system for adding a person,
which results in a person being added to the group, rather than being
invited.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.add.csv
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/

.. [#base] For adding a single person to a group see the base product
          ``gs.group.member.add.base``:
          <https://source.iopen.net/groupserver/gs.group.member.add.base>

.. [#json] See <https://source.iopen.net/groupserver/gs.group.member.add.json>

.. [#invite] See <https://source.iopen.net/groupserver/gs.group.member.invite.csv>

..  LocalWords:  CSV html csv json groupserver
