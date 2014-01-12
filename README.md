Always-Backup
==============

Python backup solution for cloud data

Download, run ./setup.py to configure paths and sync pairs,
then run service.py to start the backup.


Evernote
========
You can backup all Notebooks and Notes of an Evernote account
While the App is reviewed by Evernote only Sandbox sync is possible.
Evernote cant used as target currently

Dropbox
=======
Can be used as Source and Target for Backups

Local
=====
Local Stroge can currently only used as target

About Always Backup
===================
Currently there are only Modules for Evernote and Dropbox.

Later there will be also Facebook, Google+ etc. modules. 
The system supports sync between multipe modules of same type. 
This means you can sync Dropbox to Evernote, 
Dropox to Dropbox, Dropbox to local

But, this script is not finished yet.
Some of the todo's:
 - Web Interface Access to Evernote Files
 - Trash function for files


Needed Modules:
===============
urlib3
python-oauth2
python-dialog
