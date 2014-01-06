#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
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

import sys, pprint
import locale, dialog
from dialog import Dialog
sys.path.insert(0, './api')
locale.setlocale(locale.LC_ALL, '')
import dropbox
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from base64 import b64encode, b64decode

d = Dialog(dialog="dialog")
d.add_persistent_args(["--backtitle", "Always Backup Configuration"])

#Source: https://gist.github.com/ldx/5005528
def decode_dropbox_key(key):
    key, secret = key.split('|')
    key = b64decode(key)
    key = [ord(x) for x in key]
    secret = b64decode(secret)

    s = range(256)
    y = 0
    for x in xrange(256):
        y = (y + s[len(key)] + key[x % len(key)]) % 256
        s[x], s[y] = s[y], s[x]

    x = y = 0
    result = []
    for z in range(len(secret)):
        x = (x + 1) % 256
        y = (y + s[x]) % 256
        s[x], s[y] = s[y], s[x]
        k = s[(s[x] + s[y]) % 256]
        result.append(chr((k ^ ord(secret[z])) % 256))

    return ''.join(result).split('?', 2)

#Source: https://gist.github.com/inkedmn/5041037
def parse_evernote_query_string(authorize_url):
    uargs = authorize_url.split('?')
    vals = {}
    if len(uargs) == 1:
        raise Exception('Invalid Authorization URL')
    for pair in uargs[1].split('&'):
        key, value = pair.split('=', 1)
        vals[key] = value
    return vals


#   .--config helper-------------------------------------------------------.
#   |                      __ _         _          _                       |
#   |      ___ ___  _ __  / _(_) __ _  | |__   ___| |_ __   ___ _ __       |
#   |     / __/ _ \| '_ \| |_| |/ _` | | '_ \ / _ \ | '_ \ / _ \ '__|      |
#   |    | (_| (_) | | | |  _| | (_| | | | | |  __/ | |_) |  __/ |         |
#   |     \___\___/|_| |_|_| |_|\__, | |_| |_|\___|_| .__/ \___|_|         |
#   |                           |___/               |_|                    |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def get_config():
    #getting the config
    cfg = eval(file('config').read())
    try:
        cfg = eval(file('local.config').read())
    except:
        pass
    return cfg

def write_config(cfg):
    file('local.config', 'w').write(pprint.pformat(cfg))
#.
#   .--general config------------------------------------------------------.
    #   |                                   _                    __ _          |
    #   |    __ _  ___ _ __   ___ _ __ __ _| |   ___ ___  _ __  / _(_) __ _    |
    #   |   / _` |/ _ \ '_ \ / _ \ '__/ _` | |  / __/ _ \| '_ \| |_| |/ _` |   |
    #   |  | (_| |  __/ | | |  __/ | | (_| | | | (_| (_) | | | |  _| | (_| |   |
    #   |   \__, |\___|_| |_|\___|_|  \__,_|_|  \___\___/|_| |_|_| |_|\__, |   |
    #   |   |___/                                                     |___/    |
    #   +----------------------------------------------------------------------+
    #   |                                                                      |
    #   '----------------------------------------------------------------------'

def general_config():
    cfg = get_config()
    ncfg = cfg['global']
    code, what = d.inputbox("Storage dir (must be writeable)", init=ncfg['base_path'])
    if code == 0:
        cfg['global']['base_path'] = what
    if d.yesno("Do you want always backup running in verbose mode?") == d.DIALOG_OK:
        cfg['global']['verbose'] = True
    else:
        cfg['global']['verbose'] = False

    write_config(cfg)
    main_menu()
#.
#   .--sync pairs----------------------------------------------------------.
#   |                                               _                      |
#   |            ___ _   _ _ __   ___   _ __   __ _(_)_ __ ___             |
#   |           / __| | | | '_ \ / __| | '_ \ / _` | | '__/ __|            |
#   |           \__ \ |_| | | | | (__  | |_) | (_| | | |  \__ \            |
#   |           |___/\__, |_| |_|\___| | .__/ \__,_|_|_|  |___/            |
#   |                |___/             |_|                                 |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def edit_sync_pair(what):
    #if int we edit, string its a new one
    cfg = get_config()
    pairs = cfg.get('sync_pairs', [] )
    obj = {'name' : "", "source" : { 'name' : "", "options" : {} }, "target" : { 'name' : "", "options" : {} } }
    if type(what) == int:
        obj = pairs[what]
        # Delete the entry, we add it later as new
        del pairs[what]
        code, what = d.menu("What do you want to do?", choices= [ ("edit", "Edit the sync pair"),
                                                                  ( "delete", "Delete the sync pair" ) ] )
        if code != 0:
            sync_pairs()
        if what == "delete":
            cfg['sync_pairs'] = pairs
            write_config(cfg)
            d.msgbox("Sync pair deleted")
            sync_pairs()

    # Set Name
    code, what = d.inputbox("Name of Sync Pair", init=obj['name'])
    if code == 0:
        obj['name'] = what
    else:
        sync_pairs()
    
    # Select Source
    code, what = d.menu("From which source do you want to backup the files?",
                       choices=[ ('Evernote', 'Get all Notes from Evernote®'),
                                 ('Dropbox', 'Get all Files from Dropbox®'),
                       ])
    if code != 0:
        main_menu()
#   .--evernote------------------------------------------------------------.
#   |                                               _                      |
#   |                _____   _____ _ __ _ __   ___ | |_ ___                |
#   |               / _ \ \ / / _ \ '__| '_ \ / _ \| __/ _ \               |
#   |              |  __/\ V /  __/ |  | | | | (_) | ||  __/               |
#   |               \___| \_/ \___|_|  |_| |_|\___/ \__\___|               |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

    if what == 'Evernote':
        client = EvernoteClient(
            consumer_key = 'baschtik-3522',
            consumer_secret = '9851242b79ad58cd',
            sandbox = True #TODO
        )
        request_token = client.get_request_token('http://localhost')

        text = '''\
        1) Go to: \n%s 
        1a) Make sure that you copyed the complete URL.
        2) Click "Allow" (you might have to log in first)
        3) Copy the resulting url (starts with http://localhost) 
        ''' % client.get_authorize_url(request_token)

        d.scrollbox( text, height=15, width=200)
        try:
            old_token = obj['source']['options']['auth_token']
        except: 
            old_token = ""
        code, authurl = d.inputbox( "Now enter the URL (or don't change the entry if you don't want to relogin.", width=150, init=old_token )
        if code != 0:
            sync_pairs()

        if old_token != authurl.strip() and code == 0:
            obj['source']['name'] = "evernote"

            try:
                vals = parse_evernote_query_string(authurl)
                auth_token = client.get_access_token(
                            request_token['oauth_token'],
                            request_token['oauth_token_secret'],
                            vals['oauth_verifier']
                        )
            except:
                d.msgbox("""There was an error getting the access token\nThe profile will be saved, continue and edit it later. Otherwise sync will not work""", height=10, width=50)
                auth_token = ""

            obj['source']['options']['auth_token'] = auth_token

#.
#   .--dropbox-------------------------------------------------------------.
#   |                    _                 _                               |
#   |                 __| |_ __ ___  _ __ | |__   _____  __                |
#   |                / _` | '__/ _ \| '_ \| '_ \ / _ \ \/ /                |
#   |               | (_| | | | (_) | |_) | |_) | (_) >  <                 |
#   |                \__,_|_|  \___/| .__/|_.__/ \___/_/\_\                |
#   |                               |_|                                    |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

    elif what == 'Dropbox':
        # I dont understand the idea to conceal the keys and decode it directly after...
        # in fact, i think thats stupid but what can i do...
        app_key, app_secret = decode_dropbox_key("N6bIhPubg6A=|NUYVEbxJTEMZr5hxYsGbhAWuVqEpujqkmuCyv6MJ3A==")
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        authorize_url = flow.start()
        text = '''\
        1) Go to: \n%s 
        2) Click "Allow" (you might have to log in first)
        3) Copy the authorization code. ''' % authorize_url

        d.msgbox( text, height=15, width=95)
        try:
            old_token = obj['source']['options']['auth_token']
        except: 
            old_token = ""
        code, what = d.inputbox( "Now enter the authorization code here: ", 
                                 init=old_token )

        if old_token != what.strip() and code == 0:
            obj['source']['name'] = "dropbox"
            try:
                access_token, user_id = flow.finish(what.strip())
            except:
                d.msgbox("""There was an error contacting dropbox or you entered an invalid token\nThe profile will be saved, continue and edit it later. Otherwise sync will not work""", height=10, width=50)
                access_token = ""

            obj['source']['options']['auth_token'] = access_token

#.
    # Currently only local possible
    obj['target']['name'] = "local"
     
    pairs.append(obj)
    cfg['sync_pairs'] = pairs
    write_config(cfg)
    d.msgbox("Config Saved")
    main_menu()
    
def sync_pairs():
    cfg = get_config()
    choices = [ (str(x), y['name'] ) for x,y in enumerate( cfg.get('sync_pairs',[] )) ]
    choices.append(("new", "Create a new Sync pair"))
    code, what = d.menu("Sync Pair Configuration. Sync pairs containing all Backup configuration",
                       choices=choices)
    if code == 0:
        if what != "new":
            edit_sync_pair(int(what))
        else: 
            edit_sync_pair(what)
    main_menu()
#.
def main_menu():
    code, what = d.menu("Main",
                       choices=[("(1)", "Set general Configuration"),
                                ("(2)", "Sync Pair Configuration")])

    if code != 0:
        sys.exit()
    if what == '(1)':
        general_config()
    if what == '(2)':
        sync_pairs()

main_menu()

