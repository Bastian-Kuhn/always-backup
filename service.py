#!/usr/bin/python
import glob
import sys
import os
import time
from multiprocessing import Process
import signal

sys.path.append('./modules')

#getting the config
cfg = eval(file('config').read())
try:
    cfg = eval(file('local.config').read())
except:
    pass

#Getting all sync plugins
modules = {}
for folder in glob.glob("./plugins/*/"):
    try:
       module = folder.split('/')[-2]
       exec("import plugins.%s.main as %s" % (module, module))
       modules.update(eval(file(folder + "plugin_def").read()))
    except:
        if cfg['global']['verbose']:
            print sys.exc_info()
        pass

def service_web():
    run(host=cfg['webserver']['ip'], port=cfg['webserver']['port'], quiet=True)

def get_diff(source, target):
    missing_files = []
    if not source or not target:
        sys.stderr.write("No Data from at least one sync plugin")
        return []
    for ident, values in source:
        if values['upd_attr'] not in [ y['upd_attr'] for x, y in target ]:
            missing_files.append(( ident, values))
    return missing_files

def save_stat_file(data, folder):
    path = "%s/%s/state" % (cfg['global']['base_path'], folder)
    file(path, "w").write(str(data))

def get_update_state(folder):
    path = "%s/%s/upd_state" % (cfg['global']['base_path'], folder)
    try:
        return file(path).read()
    except:
        return False

def set_update_state(folder, state):
    path = "%s/%s/upd_state" % (cfg['global']['base_path'], folder)
    file(path, "w").write(state)

def service_sync():
    run = True
    while run:
        if len(cfg['sync_pairs']) > 0:
            for job in cfg['sync_pairs']:
                #Get sync config
                source_name = job['source']['name']
                source =  modules.get(source_name)
                if source == None:
                    sys.stderr.write("Module: %s not found. Skipping sync configuration" % source_name)
                    continue

                target_name = job['target']['name']
                target =  modules.get(target_name)
                if target == None:
                    sys.stderr.write("Module: %s not found. Skipping sync configuration" % target_name)
                    continue

                #Begin Sync
                updState = get_update_state(job['name'])
                need_sync, updState = source['init_function'](job['name'], job['source'].get('options'), cfg['global'], updState)
                set_update_state(job['name'], updState)

                target['init_function'](job['name'], job['target'].get('options'), cfg['global'])
                if need_sync:
                    remote_files = source['list_function']()
                    local_files = target['list_function']("target")
                    missing_files = get_diff(remote_files, local_files)
                    source['pull_function'](missing_files, target['push_function'])
                    save_stat_file(remote_files, job['name'])

        else:
            if cfg['global']['verbose']:
                sys.stderr.write("Sync: Nothing to do. Pleas configure at least a sync pair")

        if not cfg['global']['run_as_service']:
            run = False
            if cfg['global']['verbose']:
                print "Sync job service finished"
        else: 
            if cfg['global']['verbose']:
                print "Starting over after a 10min break"
            try:
                time.sleep(600)
            except:
                if cfg['global']['verbose']:
                    print "Have to end the Sync loop... :("
                return
            
#Including Website
execfile('./website/main.py')

#webservice = Process(target=service_web)
#webservice.deamon = True
#webservice.start()
#if cfg['global']['verbose']:
#    print "Serverstarted. You can use your browser to configure: http://%s:%s" % \
#                                (cfg['webserver']['ip'], cfg['webserver']['port']) 
#
syncservice = Process(target=service_sync)
syncservice.deamon = True
syncservice.start()

def quit(signum, frame):
    if cfg['global']['verbose']:
        print "\nThanks for using always Backup"
    try:
        sys.exit(0)
    except:
        pass

signal.signal(signal.SIGINT, quit)
