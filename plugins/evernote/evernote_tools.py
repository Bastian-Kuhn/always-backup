import os

def clean_filename(filename):
    chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(c for c in filename if c in chars)


"""Get the stats file with the list of all local saved evernote files""" 
def get_local_notes(notebook_path):
    try:
        os.makedirs(notebook_path)
    except os.error:
        pass
    if os.path.exists(notebook_path + "/stats"):
        return eval(file(notebook_path + "/stats").read())
    return {}

