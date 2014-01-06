==============================
``gs.group.member.invite.csv``
==============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Send invitations to join a group in bulk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-01-06
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This product is concerned with the *issuing* of invitations to join an
online group in *bulk* [#base]_, using a CSV file submitted to a
form_. Most of the page is powered by JavaScript_.

Form
====

The ``admin_invite_csv.html`` form, in the Group context, takes a CSV file
and invites each person in the file (one per row) to join the group. The
work is done in two main steps — parsing_ and inviting_ — which is
controlled by JavaScript_.

Parsing
-------

In the CSV file each row represents a person, and each column represents a
profile attribute. The form ``gs-group-member-invite-csv.json`` parses the
information in the CSV file and returns a JSON object: a list of profile
data. The JavaScript_ then handles the inviting_.

The parsing form is a "JSON" form, as supplied by
``gs.content.form.api.json`` [#json]_. The HTTP ``PUT`` parses in a list of
column identifiers and the CSV file, and a JSON object is returned. If
successful the object is a list of profile-objects. If there is a problem
then a JSON object is returned with ``status`` set to one of the following
error numbers, and ``message`` set to a human readable message.

=====  ======================  ===============================================
Error  Name                    Note
=====  ======================  ===============================================
-1     Form error              "Standard" ``gs.content.form.api.json`` error.
-2     Unicode Decode Error    The entire file could not be parsed.
-3     Column-count error      The column count was different to the ID count.
-4     No rows                 No rows could be found in the CSV.
=====  ======================  ===============================================

Inviting
--------

The inviting is actually carried out by ``gs.group.member.invite.json``. If
the CSV is fine then the JavaScript_ fires off invitation notifications
provided by ``gs.group.member.invite.base``. The invitation is responded to
using one of the two pages in the ``gs.profile.invite`` module [#profile]_.

JavaScript
==========

JavaScript is essential to the Invite by CSV system; without full
compliance the page simply will not work. I decided to make the JavaScript
a requirement because it **drastically** the system, reducing errors in my
code, and **drastically** improves the usability. (The usability is far
from good, but the earlier CSV Invite system would only show a spinner and
generally end up showing a *TCP Timeout* error page.) The code, provided by
the resource ``/++resource++gs-group-member-invite-csv.js``, controls the
marshalling of `user-supplied data`_, a `template generator`_, the `parsing
AJAX`_ and the `inviting AJAX`_. All are controlled by some `connecting
code`_.

User-supplied data
------------------

There are two components to the user-supplied data:

* The CSV file (which we will ignore for now) and
* The columns.

The latter is supported by the JavaScript class
``GSInviteByCSVOptionalAttributes``. The page and code provide a table at
Twitter Bootstrap ``dropdown`` that allows the group administrator to
select the optional attributes in the page. The same class can marshal the
data out of the HTML-table (embedded in the page) and into a list of
profile attributes and names. These are used by the `template generator`_
and `parsing ajax`_.

Template Generator
------------------

The template-CSV generator is provided by the
``GSInviteByCSVTemplateGenerator`` class. It examines the
profile-attributes that have been specified by the group administrator and
then generates a data-URL. This URL is then set as the ``href`` for a
(hidden) anchor element that is then added to a page. Finally, a ``click``
event is fired, which causes the browser to "download" the CSV template. 

Parsing AJAX
------------

The JavaScript that powers the parsing AJAX is one of the reasons that only
(relatively) new browsers support the *Invite by CSV* page. The class
``GSInviteByCSVParserAJAX`` makes use of the ``FormData`` [#formData]_ and
``File`` [#file]_ APIs to marshal the data out of the form and to the
parsing`_ form. 

The same code examines the return value from the parser. If a problem was
encountered then the error message is shown. Otherwise the `inviting AJAX`_
is called.

Inviting AJAX
-------------

The JavaScript code that actually invites each person is provided by the
``GSInviteByCSVInviterAJAX`` class. It maintains the list of people that
are yet to be invited, updates the progress bar when the inviting_ form
responds, and (depending on the response) updates the *New*, *Ignored* or
*Error* lists.

Connecting code
---------------

As is fairly standard for GroupServer JavaScript the page uses attributes
of the ``<script>`` element to pass data (such as URLs and element
selectors) to the JavaScript. As is also fairly standard, the JavaScript is
only initialised *after* the ``window`` has raised the ``load``
event. Events are used to connect one sequence of events (parsing the file)
with another (inviting the people).

Finally, the connecting the code is also used to reset the entire form when
the group administrator clicks on the *Reset* button.

Acknowledgements
================

The `template generator`_ code, like much that is tricky with the Web, is
helped by `Stack Overflow <http://stackoverflow.com/questions/17836273/>`_.

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

.. [#json] See <https://source.iopen.net/groupserver/gs.content.form.api.json>

.. [#formData] See <https://developer.mozilla.org/en-US/docs/Web/API/FormData>

.. [#file] See <https://developer.mozilla.org/en-US/docs/Web/API/File>

..  LocalWords:  CSV html csv
