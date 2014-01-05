#!/usr/bin/python
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


#import shutil, sys, hashlib, binascii
try:
    import dropbox
except:
    print "Error while importing api"
    raise

def write_msg(typ, msg):
    msg = msg.strip()
    if typ == "error":
        sys.stderr.write("\033[31mERROR:\033[0m\t" + msg + "\n")
    elif typ == "info":
        print "\033[34mINFO:\033[0m\t", msg
    else:
        print "\033[32mNOTICE:\033[0m\t", msg

#.
#   .--main----------------------------------------------------------------.
#   |                                       _                              |
#   |                       _ __ ___   __ _(_)_ __                         |
#   |                      | '_ ` _ \ / _` | | '_ \                        |
#   |                      | | | | | | (_| | | | | |                       |
#   |                      |_| |_| |_|\__,_|_|_| |_|                       |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'
def main(name, plugin_config, global_config, updateState, direction):
    global pool_name
    pool_name = name

    global local_cfg
    local_cfg = plugin_config

    global cfg
    cfg = global_config

    global job
    job = direction
    
    global client
    client = dropbox.client.DropboxClient(local_cfg['auth_token'])

    if cfg['verbose']:
        write_msg("notice", "Init Dropbox")
        write_msg("notice", 'Account: %s ' % client.account_info()['display_name'])

    #Currently we dont know if we have to sync without checking all files.
    #So we return always True:
    return True, True

def get_file_helper(file_list, folder='/'):
    for entry in list( client.metadata(folder)['contents'] ):
        if entry['is_dir']:
            get_file_helper(file_list, entry['path'])
        else:
            file_list.append((entry['path'], { "name"       : entry['path'].split('/')[-1],
                                               "upd_attr"   : entry['rev'],
                                               "path"       : entry['path'].rsplit('/', 1)[0],
                                               "infos"      : {} } ))



def get_file_list():
    # dropbox is the source for sync
    file_list = []
    if job == 'source':
        get_file_helper(file_list)
        return file_list
    #dropbox is the target for sync
    elif job == 'target':
        return []

def get_files(filelist, save):
    if cfg['verbose']:
        write_msg("notice", "Now Syncing the Files")

    for ident, data in filelist:
        f, metadata = client.get_file_and_metadata(ident)
        save(data["name"], data['path'], f.read()) 
        

#.
#   .--helper--------------------------------------------------------------.
#   |                    _          _                                      |
#   |                   | |__   ___| |_ __   ___ _ __                      |
#   |                   | '_ \ / _ \ | '_ \ / _ \ '__|                     |
#   |                   | | | |  __/ | |_) |  __/ |                        |
#   |                   |_| |_|\___|_| .__/ \___|_|                        |
#   |                                |_|                                   |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'
def clean_filename(filename):
    chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c for c in filename if c in chars)

#.
