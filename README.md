Always-Backup
==============

Python backup solution for cloud data

Download, run ./setup.py to configure your sync pairs,
then run service.py to start the backup.

The setup.py leads you trough the oAuth processes from the plugins
and saves a configuration file to ~/.alwas-backup/local.config

The service.py reads this configuration file and instantly start
to sync all pairs. The Sync currently is only in one direction.


Evernote
========
You can backup all Notebooks and Notes of an Evernote account.
Always Backup creates a nice html file from each note. Please keep in mind,
if you sync eg. to Dropbox and open the html file there via the webinterface, 
the internal links might not work. But if copy the files to your Harddisk everthing will work.
The reason is that Dropbox adds Auth information to each url. The urls in the html file doesn't have this
information in the urls.

Currently is the Evernote Module not working. The reason is that the App Secrets inside the app
are disabled by the Evernote. The actived a new secret for production use for me, but dont want me to
include it in a Open Source Programm. So i have to find a solution. My idea is to create a web page 
to handle the oAuth and return the Secret to copy and paste it in the setup. I'm not a big fan of this idea because in 
this way your secret token a passed through my server. But i swear in don't save the token on my server.

Dropbox
=======
The Dropbox Plugin can be used as Source and Target for Backups

Local
=====
The Local Plugin can be provieded with a path and a RegEx.
So it is possible to Backup Files based on a Regex to another plugin.
The plugin can act as source and as target for Backups

IMAP
====
The IMAP plugin is able to sync mails from one IMAP Server Folder to another Folder on another server,
EML Files from filesystem like plugin sources to IMAP,
and Mails from a Server to a filesystem like plugin target.

About Always Backup
===================
Currently there are only Modules for Evernote and Dropbox.

Later there will be also Facebook, Google+ etc. modules. 
The system supports sync between multipe modules of same type. 
This means you can sync Dropbox to Evernote, 
Dropox to Dropbox, Dropbox to local

But, this script is not finished yet.
Some of the todo's:
 - Trash function for files
 - To way sync


Needed Modules:
===============
 - urlib3
 - python-oauth2
 - python-dialog
