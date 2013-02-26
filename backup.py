#!/usr/bin/python
import os

from config import *

import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.edam.notestore import NoteStore
from evernote.api.client import EvernoteClient


def clean_filename(filename):
    chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c for c in filename if c in chars)

def backup_evernote():
    remote_notes = evernote_get_remote_notes()
    local_notes = evernote_get_local_notes('evernote/notebooks')
    evernote_sync_to_local(remote=remote_notes, local=local_notes)
    return True

"""
Get all remote notes from evernote
This function has to be called before any sync
"""
def evernote_get_remote_notes():
    client = EvernoteClient(token=cfg_evernote_auth_token, sandbox=cfg_evernote_sandbox)
    global note_store
    note_store = client.get_note_store()
    note_list = {} 
    for notebook in note_store.listNotebooks():
        guid = notebook.guid
        nbname = notebook.name
        note_list[nbname] = []
        filter = NoteStore.NoteFilter()
        filter.notebookGuid = guid
        # get a list of all nodes
        # Not finished
        noteList = note_store.findNotes(cfg_evernote_auth_token,filter,0,12)

        for n in noteList.notes:
            note_list[nbname].append((n.guid, { "title"         : n.title,
                                                "updated"       : n.updated,
                                                "content_hash"  : n.contentHash,
                                                }))
        
    return note_list 

"""Get all local saved notes """
def evernote_get_local_notes(what):
    url = cfg_backup_base_url + "/" + what
    try:
        os.makedirs(url)
    except os.error:
        pass
    if os.path.exists(url+"/stats"):
        return eval(file(url+"/stats").read())
    return {}

"""Sync all notes to local"""
def evernote_sync_to_local(remote, local):
    path = cfg_backup_base_url + "/evernote/notebooks"
    local_missing = {}

    for notebook, remote_notes in remote.items():
        local_notes = local.get(notebook) 
        #Check if complete notebook is missing
        if local_notes == None:
            if verbose:
                print "Evernote: New notebook %s" % notebook
            local_missing[notebook] = remote_notes
            continue
        local_notes = dict(local_notes)
        for remote_note_id, remote_note_data in dict(remote_notes).items():
            #Check for missing notes in notebook
            if remote_note_id not in local_notes.keys():
                if verbose:
                    print "Evernote: New Note: %s" % remote_note_data['title']
                local_missing.setdefault(notebook, [])
                local_missing[notebook].append((remote_note_id, remote_note_data))
                continue
            #Check for Changed notes
            if local_notes[remote_note_id]['updated'] != remote_note_data['updated']:
                if verbose:
                    print "Evernote: Changed Note: %s" % remote_note_data['title']
                local_missing.setdefault(notebook, [])
                local_missing[notebook].append((remote_note_id, remote_note_data))
                continue
     
    for notebook, notebook_data in local_missing.items():
        try:
            save_path = path + "/" + notebook
            os.makedirs(save_path)
        except os.error:
            pass
        if verbose:
            print "Evernote: Syncing Notebook %s: " % notebook
 
        for save_note_id, save_note_data in dict(notebook_data).items():
            if verbose:
                print "          -- %s" % save_note_data['title'] 
                  # bool withContent,
                  # bool withResourcesData,
                  # bool withResourcesRecognition,
                  # bool withResourcesAlternateData)
            note = note_store.getNote(cfg_evernote_auth_token, save_note_id, True, False, False, False)
            file(save_path + "/" + clean_filename(save_note_data['title']), "w").write(str(note.content))

        #Saving the stat file
        file(path+"/stats","w").write(str(remote))
    


backup_evernote()
