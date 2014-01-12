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


import sys
def write_msg(typ, msg):
    msg = msg.strip()
    if typ == "error":
        sys.stderr.write("\033[31mERROR:\033[0m\t" + msg + "\n")
    elif typ == "info":
        print "\033[34mINFO:\033[0m\t", msg
    else:
        print "\033[32mNOTICE:\033[0m\t", msg
try:
    import dropbox
except:
    write_msg("error",  "Cannot import api")
    raise


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

    try:
        account = client.account_info()['display_name']
    except:
        write_msg("error", "Exception getting data from Dropbox. (%s)" % local_cfg['auth_token'])
        raise

    if cfg['verbose']:
        write_msg("notice", "Init Dropbox")
        write_msg("notice", 'Account: %s ' % account )

    #Currently we dont know if we have to sync without checking all files.
    #So we return always True:
    return True, True


# Litte helper to be able to search the nested folders
def get_file_helper(file_list, folder='/'):
    files = list(file_list)
    for entry in list( client.metadata(folder)['contents'] ):
        if entry['is_dir']:
            files = get_file_helper(files, entry['path'])
        else:
            files.append((entry['path'], { "name"       : entry['path'].split('/')[-1],
                                           "upd_attr"   : entry['revision'],
                                           "path"       : entry['path'].rsplit('/', 1)[0],
                                           "infos"      : {} } ))
    return files

# Get list of files 
def get_file_list():
    print client.account_info()['display_name']
    return get_file_helper([])

def get_files(filelist, save):
    if cfg['verbose']:
        write_msg("notice", "Now Syncing the Files")

    for ident, data in filelist:
        if cfg['verbose']:
            write_msg("info","Downloading: " + ident)
        f, metadata = client.get_file_and_metadata(ident)
        save(data["name"], data['path'], f.read()) 
        
def save_file(filename, path, data):
    full_path = "/%s/%s/%s" % ( pool_name, path, filename )
    if cfg['verbose']:
        write_msg("info","Uploading: " + full_path)
    client.put_file(full_path, data, overwrite=True)
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
