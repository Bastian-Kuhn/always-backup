#!/usr/bin/python

from config import *
try:
    from config_bk import *
except:
    pass

""" Starting Evernote """
if cfg_do_evernote:
    from bk_evernote import *
    backup_evernote()

    if cfg_evernpte_html:
        if verbose:
            print "Oh, not finished, have to create the html files..."
        from bk_evernote_html import *
        evernote_generate_html_files()
        if verbose:
            print "OK, finish :)"
