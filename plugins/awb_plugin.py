#!/usr/bin/python

class awb_plugin(object):
    name = "" # Name of the Syncpair config
    local_cfg = {} # Syncpair config for directen
    cfg = {}  # global configuration options
    job = "" # Direction target/ source
    update_State = False

    def __init__(self, name, plugin_config, global_config, update_State, direction):
        self.name = name
        self.local_cfg = plugin_config
        self.cfg = global_config
        self.job = direction
        self.update_State = update_State

    def get_sync_state(self):
        return True, True

    def get_data_list(self, target, parsef ):
        return []

    def get_data(self,filelist, save):
        return False

    def save_data(self, filename, path, data):
        pass

    def parse_function(self, filehandle, path='/'):
        return False

    def close(self):
        pass
