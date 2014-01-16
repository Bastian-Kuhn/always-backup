#!/usr/bin/python
import glob, sys, os, time, datetime,  signal, pprint
#from multiprocessing import Process

#sys.path.append('./modules')
sys.path.insert(0, './api')
sys.path.insert(1, './plugins')

#getting the config
cfg = eval(file('config').read())
try:
    cfg = eval(file('local.config').read())
except:
    pass
from awb_functions import *
from awb_evernote import awb_evernote
from awb_dropbox import awb_dropbox
from awb_local import awb_local

plugins = {
 "evernote" : awb_evernote,
 "dropbox"  : awb_dropbox,
 "local"    : awb_local,
}
#   .--helper func.--------------------------------------------------------.
#   |        _          _                    __                            |
#   |       | |__   ___| |_ __   ___ _ __   / _|_   _ _ __   ___           |
#   |       | '_ \ / _ \ | '_ \ / _ \ '__| | |_| | | | '_ \ / __|          |
#   |       | | | |  __/ | |_) |  __/ |    |  _| |_| | | | | (__ _         |
#   |       |_| |_|\___|_| .__/ \___|_|    |_|  \__,_|_| |_|\___(_)        |
#   |                    |_|                                               |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

def get_diff(source, target):
    missing_files = []
    for ident, values in source:
        if values['upd_attr'] not in [ y['upd_attr'] for x, y in target ]:
            missing_files.append(( ident, values))
    return missing_files

def save_stat_file(data, folder):
    path = "%s/%s/state" % (cfg['global']['base_path'], folder)
    file(path, "w").write(str(data))

def get_stat_file(folder):
    path = "%s/%s/state" % (cfg['global']['base_path'], folder)
    try:
        return eval(file(path).read())
    except:
        return []

def get_update_state(folder):
    path = "%s/%s/upd_state" % (cfg['global']['base_path'], folder)
    try:
        return file(path).read()
    except:
        return False

def set_update_state(folder, state):
    path = "%s/%s/upd_state" % (cfg['global']['base_path'], folder)
    file(path, "w").write(state)

#.
#   .--sync service--------------------------------------------------------.
#   |                                                   _                  |
#   |        ___ _   _ _ __   ___   ___  ___ _ ____   _(_) ___ ___         |
#   |       / __| | | | '_ \ / __| / __|/ _ \ '__\ \ / / |/ __/ _ \        |
#   |       \__ \ |_| | | | | (__  \__ \  __/ |   \ V /| | (_|  __/        |
#   |       |___/\__, |_| |_|\___| |___/\___|_|    \_/ |_|\___\___|        |
#   |            |___/                                                     |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'
def service_sync():
    run = True
    while run:
        if len(cfg['sync_pairs']) > 0:
            for job in cfg['sync_pairs']:
                if job.get('disabled'):
                    if cfg['global']['debug']:
                        write_msg("debug", "Pair %s is disabled in config" % job['name'] )
                    continue
                if cfg['global']['verbose']:
                    print "\n\033[32m#### Working on '%s' ####\033[0m" % job['name']
                #Get sync config
                source_name = job['source']['name']
                target_name = job['target']['name']

                try:
                    path = "%s/%s/" % (cfg['global']['base_path'], job['name'])
                    os.makedirs(path)
                except os.error:
                    pass

                updState    = get_update_state( job['name'] )
                source = plugins[source_name]( job['name'], 
                                               job['source'].get('options'), 
                                               cfg['global'], 
                                               updState, 
                                               'source')

                need_sync, updState = source.get_sync_state() 
                #Save the last sync state 
                set_update_state(job['name'], str(updState))
                target = plugins[target_name]( job['name'], 
                                               job['target'].get('options'), 
                                               cfg['global'], 
                                               False, 
                                               'target')
                if need_sync:
                    #Get a list of the files we want to sync
                    source_files = source.get_data_list()
                    missing_files = get_diff(source_files, get_stat_file(job['name']))
                    #let source pull function push it to the target push function
                    source.get_data(missing_files, target.save_data)
                    #Save out stat file that we can compare next time
                    save_stat_file(source_files, job['name'])

        else:
            if cfg['global']['verbose']:
                write_msg("error", "Sync: Nothing to do. Pleas configure at least a sync pair")

        if not cfg['global']['run_as_service']:
            run = False
            if cfg['global']['verbose']:
                write_msg('info', "Sync job service finished" )
        else: 
            if cfg['global']['verbose']:
                write_msg("notice", "Starting over after a 10min break" )
            try:
                time.sleep(600)
            except:
                if cfg['global']['verbose']:
                    write_msg("error", "Have to end the Sync loop... :(")
                return
#.

# Start sync
service_sync()
