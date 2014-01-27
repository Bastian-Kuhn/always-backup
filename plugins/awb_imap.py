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
        passwort = self.local_cfg['passwort']
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
    def get_data_list(self):
        if self.cfg['verbose']:
            write_msg("info", "Getting list of mails (This maye take a long while)")
        files = []
        self.connect.select(self.local_cfg['folder'])
        typ, data = self.connect.search(None, 'ALL')
        for num in data[0].split():
            typ, data = self.connect.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
            msg_id =  data[0][1].strip().split()[1]
            files.append(( num, { "name"       : False, # Not known here
                                  "upd_attr"   : msg_id,
                                  "path"       : self.local_cfg['folder'],
                                }))
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

        for msg_id, data in filelist:
            if self.cfg['verbose']:
                write_msg("info","Downloading Msg: " + msg_id)
            typ, msg_data = self.connect.fetch(msg_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    subject, encoding = email.Header.decode_header(msg['subject'])[0]
                    break
            filename = str(msg_id) + "_" + subject.replace(' ','_') + ".eml"
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
        if not filename.endswith('.eml'):
            if self.cfg['debug']:
                write_msg('notice', filename + " not ending with .eml ")
            return
        if self.cfg['verbose']:
            write_msg("info","Uploading: " + filename)
        self.connect.append(self.local_cfg['folder'], '', '', str(data))
    #.
