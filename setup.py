#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
import sys, pprint
import locale, dialog
from dialog import Dialog
sys.path.insert(0, './api')
locale.setlocale(locale.LC_ALL, '')
import dropbox
from base64 import b64encode, b64decode

d = Dialog(dialog="dialog")
d.add_persistent_args(["--backtitle", "Always Backup Configuration"])

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

    key = ''.join([chr(a) for a in key])
    return ''.join(result).split('?', 2)

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

    if what == 'Evernote':
        pass
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

