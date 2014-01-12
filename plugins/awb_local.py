#!/usr/bin/python
import os, awb_plugin
from awb_functions import *
class awb_local(awb_plugin.awb_plugin):
    def __init__(self, name, plugin_config, global_config, update_State, direction):
        self.name = name
        self.local_cfg = plugin_config
        self.cfg = global_config
        self.job = direction
        self.update_State = update_State

        if self.cfg['verbose']:
            write_msg("notice", "Init local Storage...")


    def get_data_list(self):
       try:
           return eval(file("%s/%s/state" % (self.cfg['base_path'],self.name)).read())
       except:
           return []

    def save_data(self, filename, path, data):
        full_path = "%s/%s/%s" % ( self.cfg['base_path'], self.name, path )
        try:
            os.makedirs(full_path)
        except os.error:
            pass
        file("%s/%s" % (full_path, filename), "w").write(data)

