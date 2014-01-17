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
from base64 import b64encode, b64decode

d = Dialog(dialog="dialog")
d.add_persistent_args(["--backtitle", "Always Backup Configuration"])
#.
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

def find_exsisting_token(plugin):
    cfg = get_config()
    keys = []
    found_tokens = []
    if cfg.get('sync_pairs'):
        for job in cfg['sync_pairs']:
            for what in ['source', 'target']:
                if job[what]['name'] == plugin:
                    token = job[what]['options']['auth_token']
                    if token and token not in found_tokens:
                        found_tokens.append(token)
                        keys.append((job['name'], token ))
        return keys
    return False
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

def find_exsisting_token_dialog(plugin):
    tokens = find_exsisting_token(plugin)
    if tokens:
        code, what = d.menu("You can use one of the existing tokens from the "
                            "following configurations.\nIf you choice Cancel the "
                            "Auth process will be started to create a new token.",
                            choices=tokens
                            )
        for name, token in tokens:
            if name == what:
                return token
    return False

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
def auth_evernote():
    #import evernote.edam.userstore.constants as UserStoreConstants
    #import evernote.edam.type.ttypes as Types
    from evernote.api.client import EvernoteClient
    client = EvernoteClient(
        consumer_key = 'baschtik-3522',
        consumer_secret = '9851242b79ad58cd',
        sandbox = True, 
    )
    request_token = client.get_request_token('http://always-backup.com/external_auth/evernote/')

    try:
        text = '''\
        1) Go to: \n%s 
        1a) Make sure that you have the complete URL (Scroll to te right).
        2) Click "Allow" (you might have to log in first)
        3) You will get a Code. Copy it to the Clip-board 
        ''' % client.get_authorize_url(request_token)
    except:
        d.msgbox("Sorry, Evernote reportet an error. "
                 "I quit the setup and show you the Response from Evernote.")
        print request_token
        raise

    d.scrollbox( text, height=15, width=0)
    code, verifier = d.inputbox( "Now enter the code here:", width=150 )
    if code != 0:
        sync_pairs()

    try:
        auth_token = client.get_access_token(
                    request_token['oauth_token'],
                    request_token['oauth_token_secret'],
                    verifier
                )
    except:
        d.msgbox("There was an error gernerating the access token\n"
                 "The profile will be saved, continue and edit it later."
                 "Otherwise sync will not work""", height=10, width=50)
        auth_token = False
    return auth_token
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
def auth_dropbox():
    import dropbox
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
    code, what = d.inputbox( "Now enter the authorization code here: " )

    if code != 0:
        sync_pairs()
    else:
        try:
            access_token, user_id = flow.finish(what.strip())
        except:
            d.msgbox("There was an error contacting dropbox or you "
                     "entered an invalid code\nThe profile will be saved,"
                     "continue and edit it later. Otherwise sync will not work", 
                     height=10, width=50)
            access_token = False
    return access_token
#.

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
    code, which_plugin = d.menu("From which source do you want to backup the files?",
                       choices=[ ('Evernote', 'Get all Notes from Evernote®'),
                                 ('Dropbox', 'Get all Files from Dropbox®'),
                       ])
    if code != 0:
        main_menu()
    
    obj['source']['name'] = which_plugin.lower()
    token = find_exsisting_token_dialog(which_plugin.lower())
    if token:
         obj['source']['options']['auth_token'] = token
    else:
        if which_plugin == 'Evernote':
            obj['source']['options']['auth_token'] = auth_evernote()

        elif which_plugin == 'Dropbox':
            obj['source']['options']['auth_token'] = auth_dropbox()

    # Currently only local possible
    # Select Target
    code, which_plugin = d.menu("To which target do you want to backup the files?",
                       choices=[ ('Local', 'Save the files to your Hardisk'),
                                 ('Dropbox', 'Put the files to Dropbox®'),
                       ])
    if code != 0:
        main_menu()
    
    obj['target']['name'] = which_plugin.lower()
    if which_plugin in [ "Dropbox" ]:
        token = find_exsisting_token_dialog(which_plugin.lower())
        if token:
             obj['target']['options']['auth_token'] = token
        else:
            if which_plugin == 'Evernote':
                obj['target']['options']['auth_token'] = auth_evernote()

            elif which_plugin == 'Dropbox':
                obj['target']['options']['auth_token'] = auth_dropbox()
         
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

