bk\_cloudbackup
==============

Python backup solution for cloud data

Currently you can backup all Notebooks and Notes of a avernote account
All you need is the evernote python api and a api key.
Then, just take a look at the config file and run service.py

The Script will connect to evernote, load all notebooks and notes,
checks for new or updated notes, saves it in you local filesystem
and move deleted mails into a trash folder. If you want also
a simple html file is created for each note. But currently the html
feature is only a proof of concept.

But, this script is not finished yet.
Some of the todo's:
 - Create a html file whit better formating and attachments
 - Creating a web interface for configuration and access to the backuped files





