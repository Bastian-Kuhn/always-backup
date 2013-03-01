#!/usr/bin/python
import os
import sys
import glob
import shutil
import datetime

import evernote_tools

import hashlib
import binascii
try:
    import evernote.edam.userstore.constants as UserStoreConstants
    import evernote.edam.type.ttypes as Types
    from evernote.edam.notestore import NoteStore
    from evernote.api.client import EvernoteClient
except:
    print "Please install the evernote Python API"
    sys.exit(1)

def backup(config):
    global cfg
    cfg = config
    if cfg['evernote']['auth_token'] == "":
        print "Please fill in the Evernote Auth Token first (config.py)"
        sys.exit(1)

    global notebook_path
    notebook_path = cfg['backup_target'] + "/evernote/notebooks"

    if cfg['verbose']:
        print "Backup Evernote"
    remote_notes = get_remote_notes()
    local_notes = get_local_notes(notebook_path)
    sync_to_local(remote=remote_notes, local=local_notes)
    if cfg['verbose']:
        print "============ Evernote finish ============"

"""
Get all remote notes from evernote
This function has to be called before any sync
"""
def get_remote_notes():
    client = EvernoteClient(token=cfg['evernote']['auth_token'], sandbox=cfg['evernote']['sandbox'])
    global note_store
    note_store = client.get_note_store()
    note_list = {} 
    if cfg['verbose']:
        print "Getting Notebooks with list of notes"
    for notebook in note_store.listNotebooks():
        guid = notebook.guid
        nbname = notebook.name
        if cfg['verbose']:
            print " - Found Notebook %s " % nbname
        note_list[nbname] = []
        filter = NoteStore.NoteFilter()
        filter.notebookGuid = guid
        # get a list of all nodes
        # Not finished
        
        notes = 1
        start = 0
        stop = 50
        while notes > 0:
            if cfg['debug']:
                print " --  %s Notes from %d to %d (Notes %d)" % (nbname, start, stop, notes)
            noteList = note_store.findNotes(cfg['evernote']['auth_token'], filter, start, stop)
            start += 51
            stop += 100
            notes = len(noteList.notes)

            for n in noteList.notes:
                note_list[nbname].append((n.guid, { "title"         : n.title,
                                            "updated"       : n.updated,
                                            "content_hash"  : n.contentHash,
                                            }))
        if cfg['verbose']:
            print " -- Found %s entries in %s" % (len(note_list[nbname]), nbname)
            
    return note_list 

"""Sync all notes to local"""
def sync_to_local(remote, local):
    if cfg['verbose']:
        print "Now Syncing the Notes from Evernote to local"
    path = cfg['backup_target'] + "/evernote/notebooks"
    local_missing = {}
    for notebook, remote_notes in remote.items():
        local_notes = local.get(notebook) 
        #Check if complete notebook is missing
        if local_notes == None:
            if cfg['verbose']:
                print " - Theres a new one: %s (Sync complete)" % notebook
            local_missing[notebook] = remote_notes
            continue
        local_notes = dict(local_notes)
        for remote_note_id, remote_note_data in dict(remote_notes).items():
            #Check for missing notes in notebook
            if remote_note_id not in local_notes.keys():
                if cfg['verbose']:
                    print " - A new note: %s" % remote_note_data['title']
                local_missing.setdefault(notebook, [])
                local_missing[notebook].append((remote_note_id, remote_note_data))
                continue
            #Check for Changed notes
            if local_notes[remote_note_id]['updated'] != remote_note_data['updated']:
                if cfg['verbose']:
                    print " - A changed note: %s" % remote_note_data['title']
                local_missing.setdefault(notebook, [])
                local_missing[notebook].append((remote_note_id, remote_note_data))
                continue
    
    if cfg['verbose']:
        print "Download Notes"
    for notebook, notebook_data in local_missing.items():
        try:
            save_path = path + "/" + notebook
            os.makedirs(save_path)
        except os.error:
            pass
        if cfg['verbose']:
            print " - Notebook is %s: " % notebook
 
        for save_note_id, save_note_data in dict(notebook_data).items():
            if cfg['verbose']:
                print " -- %s" % save_note_data['title'] 
                  # bool withContent,
                  # bool withResourcesData,
                  # bool withResourcesRecognition,
                  # bool withResourcesAlternateData)
            note = note_store.getNote(cfg['evernote']['auth_token'], save_note_id, True, True, True, True)
            #Saving Content
            file(save_path + "/" + evernote_clean_filename(save_note_data['title']), "w").write(str(note.content))
            if cfg['evernote']['debug_dump']:
                import inspect
                file(save_path + "/" + evernote_clean_filename(save_note_data['title'] + ".dump"), "w")\
                .write(str(inspect.getmembers(note)))

            #Saving Attachments
            files = {}
            if note.resources:
                for res in note.resources:
                    files[res.guid] = {}
                    files[res.guid]['mime'] = res.mime
                    files[res.guid]['fileName'] = res.attributes.fileName
                    if res.attributes.fileName != None:
                        att_path = save_path + "/" + evernote_clean_filename(save_note_data['title'])+"-files"
                        try:
                            os.makedirs(att_path)
                        except os.error:
                            pass
                        file(att_path + "/" + evernote_clean_filename(res.attributes.fileName), "w").write(res.data.body)
                #print files

    #Saving the stat file
    file(path+"/stats","w").write(str(remote))
    
    deleted_notebooks = []
    deleted_notes = {}
    for notebook, local_notes in local.items(): 
        remote_notes = remote.get(notebook)
        if remote_notes == None:
            deleted_notebooks.append(notebook)
        else:
            remote_notes = dict(remote_notes)
            for local_note_id, local_note_data  in dict(local_notes).items():
                if local_note_id not in remote_notes.keys():
                    deleted_notes.setdefault(notebook, [])
                    deleted_notes[notebook].append((local_note_id, local_note_data))
    if len(deleted_notebooks) > 0 or len(deleted_notes.keys()) > 0:
        if cfg['verbose']:
            print "Move deleted Notes to trash"
        time = datetime.datetime.now() 
        backup_path = cfg_backup_base_url + "/evernote/trash/" + time.strftime("%Y-%m-%d") 
        try:
            os.makedirs(backup_path)
        except:
            pass
        if cfg['verbose']:
            print " - New Trash Path is %s" % backup_path
        #TBD: Stats file is missing in this case    
        for notebook in deleted_notebooks:
            os.renames(path + "/" + notebook, backup_path + "/" + notebook)

        for notebook, filedata in deleted_notes.items():
            try:
                os.makedirs(backup_path + "/"  + notebook)
            except:
                pass
            for note_id, note_data in filedata:
                nname = clean_filename(note_data['title'])
                source_path = "%s/%s/%s" % (path, notebook, nname)
                target_path = "%s/%s/" % (backup_path, notebook)
                print " - %s to %s " % (source_path, target_path)
                for mfile in glob.glob(source_path+"*"):
                    if cfg['verbose']:
                        print " - Moving %s to trash " % nname
                    shutil.move(mfile, target_path)

        if os.path.exists(backup_path+"/stats"):
            old = eval(file(backup_path+"/stats").read())
            for nb, data in old.items():
                deleted_notes.setdefault(nb, [])
                deleted_notes[nb] = deleted_notes[nb] + data
        file(backup_path+"/stats", "w").write(str(deleted_notes))       



