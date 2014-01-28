#!/usr/bin/python
#-*- coding:utf-8 -*-
import awb_plugin
from awb_functions import *

import imaplib, email

class awb_imap(awb_plugin.awb_plugin):
    connect = False

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

        user = self.local_cfg['user']
        passwort = self.local_cfg['password']
        server = self.local_cfg['server']

        try:
            self.connect = imaplib.IMAP4_SSL(server)
            self.connect.login( user, passwort )
        except:
            write_msg("error", "Cannot connect to: imaps://%s@%s " % ( user, server ) )
            raise

        if self.cfg['verbose']:
            write_msg("notice", "Connected imaps://%s@%s" % ( user, server ) )
    #.

    # The parse function is be called from inside (get_data_list)
    # and also from outsite, if a plugin has to sync emal files to imap.
    # If we called it from inside we need num, the message num.
    # num is the id we need to download the mail in the next stept.
    def parse_function(self, filehandle, filename, path, num=False):
        if type(filehandle) == file:
            msg = email.message_from_file(filehandle)
        else:
            msg = email.message_from_string(filehandle)
        if not filename:
            filename = msg['MESSAGE-ID']
        return ( filename, { "name"        : email.Header.decode_header(msg['subject'])[0][0],
                             "upd_attr"    : msg['MESSAGE-ID'],
                             "path"        : path,
                             'download_id' : num,
                                    })
    #   .--get data list-------------------------------------------------------.
    #   |                    _         _       _          _ _     _            |
    #   |          __ _  ___| |_    __| | __ _| |_ __ _  | (_)___| |_          |
    #   |         / _` |/ _ \ __|  / _` |/ _` | __/ _` | | | / __| __|         |
    #   |        | (_| |  __/ |_  | (_| | (_| | || (_| | | | \__ \ |_          |
    #   |         \__, |\___|\__|  \__,_|\__,_|\__\__,_| |_|_|___/\__|         |
    #   |         |___/                                                        |
    #   +----------------------------------------------------------------------+
    #   |                                                                      | 
    #   '----------------------------------------------------------------------'
    def get_data_list(self, target, parsef ):
        # TODO: There must be a way to speed up here.
        # E.g: Get list and Get data mixed together.
        # But this may leads to problems in plugins like evernote.
        # I have to think about it...
        if self.cfg['verbose']:
            write_msg("info", "Getting list of mails (This maye take a long time)")
        files = []
        folder = "INBOX"
        if self.local_cfg['folder'] != "":
            folder = self.local_cfg['folder']
        self.connect.select(folder)
        typ, data = self.connect.search(None, 'ALL')
        for num in data[0].split():
            typ, data = self.connect.fetch(num, '(BODY[HEADER])')
            files.append( self.parse_function( data[0][1], False, self.local_cfg['folder'], num ) )
        return files

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

        for name, data in filelist:
            if self.cfg['verbose']:
                write_msg("info","Downloading Msg: " + name)
            msg_id = data['download_id']
            typ, msg_data = self.connect.fetch(msg_id, '(RFC822)')
            filename = str(msg_id) + "_" + clean_filename(data['name']) + ".eml"
            save(filename, data['path'], msg_data[0][1]) 
    #.
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
        if self.cfg['verbose']:
            write_msg("info","Uploading: " + filename)
        self.connect.append(self.local_cfg['folder'], '', '', str(data))
    #.

    def close(self):
        self.connect.logout()
