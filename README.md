Always-Backup
==============

Python backup solution for cloud data

Currently you can backup all Notebooks and Notes of an Evernote account
All you need is the Evernote python api and a api key.
After staring service.py change to your browser and configure.
Currently you cant configure the sync pairs. But this will follow in the next days.

The Script will connect to Evernote, load all notebooks and notes,
checks for new or updated notes, saves it in you local filesystem
and move deleted mails into a trash folder.

The system is module based. Currently there is only a local and an evernote module.
Also only Evernote to local backup is possible.

Later there will be also a Dropbox, Facebook, Google+ etc. modules. 
The system will support also sync between multipe modules of same type. 
This means later you can sync Evernote to Evernote or Dropbox to Evernote, 
Dropox to Dropbox...

The next step for this tool is a webinterface (no Apache etc needed), to configure
the modules, configure sync pairs and access the files.

But, this script is not finished yet.
Some of the todo's:
 - Creating a web interface for configuration and access to the backed-up files
 - Web Interface Access to Evernote Files
 - Trash function for files
