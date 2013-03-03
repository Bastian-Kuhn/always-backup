#!/usr/bin/python
import os
import sys
import glob
import shutil
import datetime

import evernote_tools as et

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

def main(name, plugin_config, global_config):
    global config_name
    config_name = name

    global local_cfg
    local_cfg = plugin_config

    global cfg
    cfg = global_config

    if cfg['verbose']:
        print "Init Evernote..."

"""
Get a list of all all remote notes from evernote
This function has to be called before any sync, because
it inits the note_store
"""
def get_note_list():
    client = EvernoteClient(token=local_cfg['auth_token'], sandbox=local_cfg['sandbox'])

    global note_store
    try:
        note_store = client.get_note_store()
    except:
        print "Error getting notes from evernote"
        return False

    file_list = [] 
    if cfg['verbose']:
        print "Getting Notebooks with list of notes"
    for notebook in note_store.listNotebooks():
        guid = notebook.guid
        nbname = notebook.name
        if cfg['verbose']:
            print " - Found Notebook %s " % nbname
        filter = NoteStore.NoteFilter()
        filter.notebookGuid = guid

        # get a list of all nodes
        notes = 1
        start = 0
        stop = 50
        while notes > 0:
            if cfg['debug']:
                print " --  %s Notes from %d to %d (Notes %d)" % (nbname, start, stop, notes)
            noteList = note_store.findNotes(local_cfg['auth_token'], filter, start, stop)
            start += 51
            stop += 100
            notes = len(noteList.notes)

            for n in noteList.notes:
                resource_list = []
                if n.resources != None:
                    for res in n.resources:
                        resource_list.append({
                             "name"     : res.attributes.fileName,
                             "type"     : None,
                             "mime"     : res.mime,
                             "date"     : None, 
                             "change"   : None,
                            })
                file_list.append((n.guid , {
                                            "name"         : n.title,
                                            "path"         : nbname,
                                            "date"         : n.created,
                                            "change"       : n.updated,
                                            "subparts"     : resource_list,
                                            "infos"        : {
                                                "longitude"     : n.attributes.longitude,
                                                "latitude"      : n.attributes.latitude,
                                                "lastEditedBy"  : n.attributes.lastEditedBy,

                                                },
                                           }))
    return file_list 

"""Sync all notes to local"""
def pull_notes(filelist, save):
    if cfg['verbose']:
        print "Now Syncing the Notes from Evernote to local"

    for ident, data in filelist:
        if cfg['verbose']:
            print " -- %s" % data['name'] 
        note = note_store.getNote(local_cfg['auth_token'], ident, True, True, True, True)
        nbname = et.clean_filename(data['path'])
        note_name = et.clean_filename(data['name'])
        save(note_name+"-content.xml", nbname, str(note.content))
        #Saving Attachments
        if note.resources:
            for res in note.resources:
                if res.attributes.fileName != None:
                    filename = et.clean_filename(res.attributes.fileName)
                    save(filename, "%s/%s-files" % (nbname, note_name), res.data.body) 
        

       # deleted_notebooks = []
       # deleted_notes = {}
       # for notebook, local_notes in local.items(): 
       #     remote_notes = remote.get(notebook)
       #     if remote_notes == None:
       #         deleted_notebooks.append(notebook)
       #     else:
       #         remote_notes = dict(remote_notes)
       #         for local_note_id, local_note_data  in dict(local_notes).items():
       #             if local_note_id not in remote_notes.keys():
       #                 deleted_notes.setdefault(notebook, [])
       #                 deleted_notes[notebook].append((local_note_id, local_note_data))
       # if len(deleted_notebooks) > 0 or len(deleted_notes.keys()) > 0:
       #     if cfg['verbose']:
       #         print "Move deleted Notes to trash"
       #     time = datetime.datetime.now() 
       #     backup_path = cfg_backup_base_url + "/evernote/trash/" + time.strftime("%Y-%m-%d") 
       #     try:
       #         os.makedirs(backup_path)
       #     except:
       #         pass
       #     if cfg['verbose']:
       #         print " - New Trash Path is %s" % backup_path
       #     #TBD: Stats file is missing in this case    
       #     for notebook in deleted_notebooks:
       #         os.renames(path + "/" + notebook, backup_path + "/" + notebook)

       #     for notebook, filedata in deleted_notes.items():
       #         try:
       #             os.makedirs(backup_path + "/"  + notebook)
       #         except:
       #             pass
       #         for note_id, note_data in filedata:
       #             nname = clean_filename(note_data['title'])
       #             source_path = "%s/%s/%s" % (path, notebook, nname)
       #             target_path = "%s/%s/" % (backup_path, notebook)
       #             print " - %s to %s " % (source_path, target_path)
       #             for mfile in glob.glob(source_path+"*"):
       #                 if cfg['verbose']:
       #                     print " - Moving %s to trash " % nname
       #                 shutil.move(mfile, target_path)

       #     if os.path.exists(backup_path+"/stats"):
       #         old = eval(file(backup_path+"/stats").read())
       #         for nb, data in old.items():
       #             deleted_notes.setdefault(nb, [])
       #             deleted_notes[nb] = deleted_notes[nb] + data
       #     file(backup_path+"/stats", "w").write(str(deleted_notes))       



