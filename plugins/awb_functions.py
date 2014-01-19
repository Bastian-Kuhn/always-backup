import sys

def write_msg(typ, msg):
    msg = msg.strip()
    if typ == "error":
        sys.stderr.write("\033[31mERROR:\033[0m\t" + msg + "\n" )
    elif typ == "info":
        print "\033[34mINFO:\033[0m\t", msg
    elif typ == "debug":
        print "\033[34mDEBUG: %s\033[0m\t" % msg
    else:
        print "\033[32mNOTICE:\033[0m\t", msg

def clean_filename(filename):
    chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c for c in filename if c in chars)
