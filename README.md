Always-Backup
==============

Python backup solution for cloud data

Currently you can backup all Notebooks and Notes of a avernote account
All you need is the evernote python api and a api key.
Then, just take a look at the config file and run service.py

The Script will connect to evernote, load all notebooks and notes,
checks for new or updated notes, saves it in you local filesystem
and move deleted mails into a trash folder.

The system is module based. Currently there is only a local and an evernote module.
Also only evernote to local backup is possible.

Later there will be also a Dropbox, Facebook, Google+ etc. modules. 
The system will support also sync between multipe modules of same type. 
This means later you can sync evernote to evernote or dropbox to evernote, 
dropox to dropbox...

The next step for this tool is a webinterface (no Apache etc needed), to configure
the modules, configure sync pairs and access the files.

But, this script is not finished yet.
Some of the todo's:
 - Creating a web interface for configuration and access to the backuped files
 - Web Interface Access to Evernote Files
 - Trash function for files
