#!/usr/bin/python
import os

def main(name, plugin_config, global_config):
    global config_name
    config_name = name

    global local_cfg
    local_cfg = plugin_config

    global cfg
    cfg = global_config

    if cfg['verbose']:
        print "Init Local..."



def list_files(part="source"):
    #if remote target, deliver local state
    if part == "target":
        try:
            return eval(file("%s/%s/state" % (cfg['base_path'],config_name)).read())
        except:
            return []
        
    #else read the file list
    elif part == "source":
        return []
    else:
        return None


def save_file(filename, path, data):
    full_path = "%s/%s/%s" % ( cfg['base_path'], config_name, path )
    try:
        os.makedirs(full_path)
    except os.error:
        pass
    file("%s/%s" % (full_path, filename), "w").write(data)

