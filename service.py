#!/usr/bin/python
import glob
import sys
import time

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

def get_diff(source, target):
    missing_files = []
    for ident, values in source:
        if ident not in [ x for x, y in target ]:
            missing_files.append(( ident, values))
    return missing_files

def save_stat_file(data, folder):
    path = "%s/%s/state" % (cfg['global']['base_path'], folder)
    file(path, "w").write(str(data))

run = True
while run == True:
    for job in cfg['sync_pairs']:
        #Get sync config
        source_name = job['source']['name']
        source =  modules.get(source_name)
        if source == None:
            print "Module: %s not found. Skipping sync configuration" % source_name
            continue

        target_name = job['target']['name']
        target =  modules.get(target_name)
        if target == None:
            print "Module: %s not found. Skipping sync configuration" % target_name
            continue

        #Begin Sync
        source['init_function'](job['name'], job['source'].get('options'), cfg['global'])
        target['init_function'](job['name'], job['target'].get('options'), cfg['global'])
        remote_files = source['list_function']()
        local_files = target['list_function']("target")
        missing_files = get_diff(remote_files, local_files)
        source['pull_function'](missing_files, target['push_function'])
        save_stat_file(remote_files, job['name'])

    if not cfg['global']['run_as_service']:
        run = False
    else: 
        time.sleep(600)


