Always-Backup
==============

Python backup solution for cloud data



Evernote
========
You can backup all Notebooks and Notes of an Evernote account
All you need is the Evernote python api and a api key.

The Script will connect to Evernote, load all notebooks and notes,
checks for new or updated notes, saves it in you local filesystem
and move deleted mails into a trash folder.

Dropbox
=======
It is possbile to Backup all File from a Dropbox account.
Sadly you have to create a Dropbox App first and provide
Always Backup with the App Secret and App Key. In ./helper you will
find a dropbox_auth.py. With this programm will return the auth_token you
need for the sync_pair configuration.


About Always Backup
===================
Currently there are only Modules for Evernote and Dropbox.
Also it's only possible to sync from remote to local.

Later there will be also Facebook, Google+ etc. modules. 
The system will (later) support also sync between multipe modules of same type. 
This means you can sync Evernote to Evernote or Dropbox to Evernote, 
Dropox to Dropbox...

But, this script is not finished yet.
Some of the todo's:
 - Creating a web interface for configuration and access to the backed-up files
 - Web Interface Access to Evernote Files
 - Trash function for files
