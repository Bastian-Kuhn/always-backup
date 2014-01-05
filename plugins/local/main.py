#!/usr/bin/python
import os

def write_msg(typ, msg):
    msg = msg.strip()
    if typ == "error":
        sys.stderr.write("\033[31mERROR:\033[0m\t" + msg + "\n" )
    elif typ == "info":
        print "\033[34mINFO:\033[0m\t", msg
    else:
        print "\033[32mNOTICE:\033[0m\t", msg

def main(name, plugin_config, global_config, updState, direction):

    global job
    job = direction

    global config_name
    config_name = name

    global local_cfg
    local_cfg = plugin_config

    global cfg
    cfg = global_config

    if cfg['verbose']:
        write_msg("notice", "Init local Storage...")
    #Need currently always a sync
    return True, ''



def list_files():
    #if remote target, deliver local state
    if job == "target":
        try:
            return eval(file("%s/%s/state" % (cfg['base_path'],config_name)).read())
        except:
            return []
        
    #else read the file list
    elif job == "source":
        return []
    else:
        return None

def get_files(filelist, save):
    pass

def save_file(filename, path, data):
    full_path = "%s/%s/%s" % ( cfg['base_path'], config_name, path )
    try:
        os.makedirs(full_path)
    except os.error:
        pass
    file("%s/%s" % (full_path, filename), "w").write(data)

