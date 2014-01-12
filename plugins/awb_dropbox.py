#!/usr/bin/python
import awb_plugin
from awb_functions import *
try:
    import dropbox
except:
    write_msg("error",  "Cannot import api")
    raise


class awb_dropbox(awb_plugin.awb_plugin):
    client = False

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
        self.client = dropbox.client.DropboxClient(self.local_cfg['auth_token'])

        try:
            account = self.client.account_info()['display_name']
        except:
            write_msg("error", "Exception getting data from Dropbox.")
            raise

        if self.cfg['verbose']:
            write_msg("notice", "Init Dropbox")
            write_msg("notice", 'Using Account: %s ' % account )
    #.
    #   .--get data list-------------------------------------------------------.
    #   |                    _         _       _          _ _     _            |
    #   |          __ _  ___| |_    __| | __ _| |_ __ _  | (_)___| |_          |
    #   |         / _` |/ _ \ __|  / _` |/ _` | __/ _` | | | / __| __|         |
    #   |        | (_| |  __/ |_  | (_| | (_| | || (_| | | | \__ \ |_          |
    #   |         \__, |\___|\__|  \__,_|\__,_|\__\__,_| |_|_|___/\__|         |
    #   |         |___/                                                        |
    #   +----------------------------------------------------------------------+
    #   |   Get a list of all files                                            |
    #   '----------------------------------------------------------------------'

    # Litte helper to be able to search the nested folders
    def get_file_helper(self, file_list, folder='/'):
        files = list(file_list)
        for entry in list( self.client.metadata(folder)['contents'] ):
            if entry['is_dir']:
                files = self.get_file_helper(files, entry['path'])
            else:
                files.append((entry['path'], { "name"       : entry['path'].split('/')[-1],
                                               "upd_attr"   : entry['revision'],
                                               "path"       : entry['path'].rsplit('/', 1)[0],
                                               "infos"      : {} } ))

        return files

    def get_data_list(self):
        return self.get_file_helper([])

    #.
    #   .--get data------------------------------------------------------------.
    #   |                           _         _       _                        |
    #   |                 __ _  ___| |_    __| | __ _| |_ __ _                 |
    #   |                / _` |/ _ \ __|  / _` |/ _` | __/ _` |                |
    #   |               | (_| |  __/ |_  | (_| | (_| | || (_| |                |
    #   |                \__, |\___|\__|  \__,_|\__,_|\__\__,_|                |
    #   |                |___/                                                 |
    #   +----------------------------------------------------------------------+
    #   | Get data from Dropbox                                                |
    #   '----------------------------------------------------------------------'
    def get_data(self, filelist, save):
        if self.cfg['verbose']:
            write_msg("notice", "Now Syncing the Files")

        for ident, data in filelist:
            if self.cfg['verbose']:
                write_msg("info","Downloading: " + ident)
            f, metadata = self.client.get_file_and_metadata(ident)
            save(data["name"], data['path'], f.read()) 
    #.
    #   .--save data-----------------------------------------------------------.
    #   |                                       _       _                      |
    #   |             ___  __ ___   _____    __| | __ _| |_ __ _               |
    #   |            / __|/ _` \ \ / / _ \  / _` |/ _` | __/ _` |              |
    #   |            \__ \ (_| |\ V /  __/ | (_| | (_| | || (_| |              |
    #   |            |___/\__,_| \_/ \___|  \__,_|\__,_|\__\__,_|              |
    #   |                                                                      |
    #   +----------------------------------------------------------------------+
    #   |  Save data to Dropbox                                                |
    #   '----------------------------------------------------------------------'
    def save_data(self, filename, path, data):
        full_path = "/%s/%s/%s" % ( self.name, path, filename )
        if self.cfg['verbose']:
            write_msg("info","Uploading: " + full_path)
        self.client.put_file(full_path, data, overwrite=True)
    #.
