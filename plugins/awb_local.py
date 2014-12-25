#!/usr/bin/python
import os, re, awb_plugin
from awb_functions import *
class awb_local(awb_plugin.awb_plugin):
    def __init__(self, name, plugin_config, global_config, update_State, direction):
        self.name = name
        self.local_cfg = plugin_config
        self.cfg = global_config
        self.job = direction
        self.update_State = update_State

        if self.cfg['verbose']:
            write_msg("notice", "Init local Storage " + plugin_config['storage_path'] + "...")


    def get_data_list(self, target, parsef):
        if self.cfg['verbose']:
            write_msg("info", "Getting list of local files")
        file_list = []
        pattern = False
        if self.local_cfg.get('regex_match') and self.local_cfg['regex_match'] != '':
            pattern = re.compile( self.local_cfg['regex_match'] )
        if target in ['imap']:
            if self.cfg['verbose']:
                write_msg("notice", "I have to use a parsing function. So scanning of the files will take longer")
        for root, _, files in os.walk(self.local_cfg['storage_path']):
            for f in files:
                fname = os.path.join(root, f)
                if pattern and not re.match(pattern, fname):
                    continue
                filename = fname.split('/')[-1]
                path = fname.rsplit('/', 1)[0]
                # Paths are always relative to the target_plugin.
                rpath = path.replace(self.local_cfg['storage_path'], '') 
                if target == 'imap':
                    file_list.append( parsef(file(fname), filename, rpath) )
                else:
                    # Normal Filesystem listing with last modification time as upd_attribte
                    try:
                        stat = str(os.stat(fname).st_mtime)
                    except:
                        if self.cfg['debug']:
                            write_msg("debug", "Cannot stat: " + fname )
                        continue

                    # So we have to replace the storage path to be compatible
                    # whit other plugins
                    file_list.append((fname, { "name"       : filename, 
                                               "upd_attr"   : stat,
                                               "path"       : rpath,
                                               "infos"      : {} } ))
        return file_list

    #   .--save data-----------------------------------------------------------.
    #   |                                       _       _                      |
    #   |             ___  __ ___   _____    __| | __ _| |_ __ _               |
    #   |            / __|/ _` \ \ / / _ \  / _` |/ _` | __/ _` |              |
    #   |            \__ \ (_| |\ V /  __/ | (_| | (_| | || (_| |              |
    #   |            |___/\__,_| \_/ \___|  \__,_|\__,_|\__\__,_|              |
    #   |                                                                      |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'
    def save_data(self, filename, path, data):
        full_path = "%s/%s" % ( self.local_cfg['storage_path'], path )
        try:
            os.makedirs(full_path)
        except os.error:
            pass
        if self.cfg['verbose']:
            write_msg("info","Saving: " + full_path + "/" + filename)
        file("%s/%s" % (full_path, filename), "w").write(data)
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
            write_msg("notice", "Now Syncing the Files")

        for ident, data in filelist:
            if self.cfg['verbose']:
                write_msg("info","Getting: " + ident)
            f = file("%s/%s" % ( data['path'], ident)) 
            save(data["name"], data['path'], f.read()) 
    #.
