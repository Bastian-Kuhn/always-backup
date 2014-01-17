#!/usr/bin/python
#   .--import--------------------------------------------------------------.
#   |                  _                            _                      |
#   |                 (_)_ __ ___  _ __   ___  _ __| |_                    |
#   |                 | | '_ ` _ \| '_ \ / _ \| '__| __|                   |
#   |                 | | | | | | | |_) | (_) | |  | |_                    |
#   |                 |_|_| |_| |_| .__/ \___/|_|   \__|                   |
#   |                             |_|                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'
import awb_plugin
from awb_functions import *
from BeautifulSoup import  BeautifulSoup
import shutil, sys, hashlib, binascii, re
try:
    import evernote.edam.userstore.constants as UserStoreConstants
    import evernote.edam.type.ttypes as Types
    from evernote.edam.notestore import NoteStore
    from evernote.api.client import EvernoteClient
except:
    print "Error while importing evernote api"
    raise
#.
class awb_evernote(awb_plugin.awb_plugin):
    client = None
    note_store = None
    #   .--init----------------------------------------------------------------.
    #   |                            _       _ _                               |
    #   |                           (_)_ __ (_) |_                             |
    #   |                           | | '_ \| | __|                            |
    #   |                           | | | | | | |_                             |
    #   |                           |_|_| |_|_|\__|                            |
    #   |                                                                      |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'
    def __init__(self, name, plugin_config, global_config, update_State, direction):
        self.name = name
        self.local_cfg = plugin_config
        self.cfg = global_config
        self.job = direction
        self.update_State = update_State

        if self.cfg['verbose']:
            write_msg("notice", "Init Evernote")

        self.client = EvernoteClient(token=self.local_cfg['auth_token'], sandbox=True)
        if self.cfg['verbose']:
            write_msg("info"," Connected to Evernote.")
        self.note_store = self.client.get_note_store()
    #.
    #   .--get sync state------------------------------------------------------.
    #   |               _                                _        _            |
    #   |     __ _  ___| |_   ___ _   _ _ __   ___   ___| |_ __ _| |_ ___      |
    #   |    / _` |/ _ \ __| / __| | | | '_ \ / __| / __| __/ _` | __/ _ \     |
    #   |   | (_| |  __/ |_  \__ \ |_| | | | | (__  \__ \ || (_| | ||  __/     |
    #   |    \__, |\___|\__| |___/\__, |_| |_|\___| |___/\__\__,_|\__\___|     |
    #   |    |___/                |___/                                        |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'
    def get_sync_state(self):
        try:
            #Check if we neet to sync
            if self.job == "source":
                sync_state = str(self.note_store.getSyncState().updateCount)
                if sync_state != self.update_State:
                    if self.cfg['verbose']:
                        write_msg("info","New Data, we have to sync (%s)" % sync_state)
                    return True, sync_state
                return False, sync_state

        except Exception as e:
            write_msg('error', e.message)
            return False
    #.
    #   .--get data list-------------------------------------------------------.
    #   |                    _         _       _          _ _     _            |
    #   |          __ _  ___| |_    __| | __ _| |_ __ _  | (_)___| |_          |
    #   |         / _` |/ _ \ __|  / _` |/ _` | __/ _` | | | / __| __|         |
    #   |        | (_| |  __/ |_  | (_| | (_| | || (_| | | | \__ \ |_          |
    #   |         \__, |\___|\__|  \__,_|\__,_|\__\__,_| |_|_|___/\__|         |
    #   |         |___/                                                        |
    #   +----------------------------------------------------------------------+
    #   |   Get a list of all all remote notes from evernote                   |
    #   '----------------------------------------------------------------------'
    def get_data_list(self):
        file_list = [] 
        if self.cfg['verbose']:
            write_msg("info", "Getting Notebooks with list of notes")
        for notebook in self.note_store.listNotebooks():
            guid = notebook.guid
            nbname = notebook.name
            if self.cfg['verbose']:
                write_msg("info", "- Found Notebook %s " % nbname)
            filter = NoteStore.NoteFilter()
            filter.notebookGuid = guid

            # get a list of all nodes
            notes = 1
            start = 0
            stop = 50
            while notes > 0:
                if self.cfg['debug']:
                    write_msg("debug", "%s Notes from %d to %d (Notes %d)" % (nbname, start, stop, notes))
                noteList = self.note_store.findNotes(self.local_cfg['auth_token'], filter, start, stop)
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
                                                "upd_attr"     : n.updateSequenceNum,
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
    #.

    def get_resource_objid(self, content):
        bs = BeautifulSoup(str(content))
        return bs.find('recoindex')['objid']


    def format_attachments(self, note, note_name):
        if not note.resources:
            return ""
        count = 0
        links = 'Attachments:<ul class="attachments">'
        for res in note.resources:
            if res.attributes.fileName != None:
                filename = clean_filename(res.attributes.fileName)
                try:
                    link = self.get_resource_objid(res.recognition.body)
                except:
                    link = filename
                count += 1
                links += u'<a href="./%s-files/%s">%s</a>' % \
                (note_name, link, filename)
        links += "</ul> (%s) " % count
        if count > 0:
            return links
        return ""



    def format_content(self, note):
        bs = BeautifulSoup(note.content)
        note_name = clean_filename(note.title)
        content = str(bs.find("en-note"))
        content = re.sub(r'<en-media.*?hash="(.*)".*?</en-media>', 
                         r'<img src="%s-files/\1">' % note_name, 
                         content )
        html = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
               "http://www.w3.org/TR/html4/loose.dtd">
               <html>
            <head>
            <title>%s</title>
            <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=utf-8">
            </head>
            <body>
               %s
              <br>
                %s
            </body>
            </html>''' % (
                note_name,
                content,
                self.format_attachments(note, note_name)

            )
        return html
    #.
    #   .--get data------------------------------------------------------------.
    #   |                           _         _       _                        |
    #   |                 __ _  ___| |_    __| | __ _| |_ __ _                 |
    #   |                / _` |/ _ \ __|  / _` |/ _` | __/ _` |                |
    #   |               | (_| |  __/ |_  | (_| | (_| | || (_| |                |
    #   |                \__, |\___|\__|  \__,_|\__,_|\__\__,_|                |
    #   |                |___/                                                 |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'
    def get_data(self, filelist, save):
        if self.cfg['verbose']:
            write_msg("info", "Getting the notes from Evernote")

        for ident, data in filelist:
            if self.cfg['verbose']:
                write_msg("info", "Downloaded %s from Evernote" % data['name'])
            note = self.note_store.getNote(self.local_cfg['auth_token'], ident, True, True, True, True)
            nbname = clean_filename(data['path'])
            note_name = clean_filename(data['name'])
            save(note_name+".html", nbname, self.format_content(note))
            if self.cfg['debug']:
                save(note_name+".debug", nbname, str(note))
            #Saving Attachments
            if note.resources:
                for res in note.resources:
                    if not res.recognition and not res.attributes.fileName:
                        continue
                    else:
                        try:
                            filename = self.get_resource_objid(res.recognition.body)
                        except:
                            filename = clean_filename(res.attributes.fileName)
                    save(filename, "%s/%s-files" % (nbname, note_name), res.data.body) 
    #.
    #   .--trash---------------------------------------------------------------.
    #   |                       _                 _                            |
    #   |                      | |_ _ __ __ _ ___| |__                         |
    #   |                      | __| '__/ _` / __| '_ \                        |
    #   |                      | |_| | | (_| \__ \ | | |                       |
    #   |                       \__|_|  \__,_|___/_| |_|                       |
    #   |                                                                      |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'
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

#.
