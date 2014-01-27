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


    def get_data_list(self):
        file_list = []
        pattern = False
        if self.local_cfg.get('regex_match') and self.local_cfg['regex_match'] != '':
            pattern = re.compile( self.local_cfg['regex_match'] )

        for root, _, files in os.walk(self.local_cfg['storage_path']):
            for f in files:
                fname = os.path.join(root, f)
                if pattern and not re.match(pattern, fname):
                    continue
                try:
                    stat = str(os.stat(fname).st_atime)
                except:
                    if self.cfg['debug']:
                        write_msg("debug", "Cannot stat: " + fname )
                    continue
                 
                file_list.append((fname, { "name"       : fname.split('/')[-1],
                                       "upd_attr"   : stat,
                                       "path"       : fname.rsplit('/', 1)[0],
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
            f = file(ident) 
            save(data["name"], data['path'], f.read()) 
    #.
