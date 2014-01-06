Always-Backup
==============

Python backup solution for cloud data



Evernote
========
You can backup all Notebooks and Notes of an Evernote account
All you need is a api key from evernote.

The Script will connect to Evernote, load all notebooks and notes,
checks for new or updated notes, saves it in you local filesystem
and move deleted mails into a trash folder.

Dropbox
=======
It is possbile to Backup all File from a Dropbox account.
In ./helper you will find a dropbox_auth.py. This programm will return the auth_token you
need for the sync_pair configuration.


About Always Backup
===================
Currently there are only Modules for Evernote and Dropbox.
Also it's only possible to sync from remote to local.

Later there will be also Facebook, Google+ etc. modules. 
The system (also later) will support sync between multipe modules of same type. 
This means you can sync Evernote to Evernote or Dropbox to Evernote, 
Dropox to Dropbox...

But, this script is not finished yet.
Some of the todo's:
 - Configuration interface (cli)
 - Web Interface Access to Evernote Files
 - Trash function for files
