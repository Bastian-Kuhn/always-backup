#!/usr/bin/python

#getting the config
cfg = eval(file('config').read())
try:
    cfg = eval(file('local.config').read())
except:
    pass

run = True
while run == True:
    """ Starting Evernote """
    if cfg['evernote']['do']:
        import plugins.evernote.backup as en 
        en.backup(cfg)

        if cfg_evernpte_html:
            if cfg['verbose']:
                print "Oh, not finished, have to create the html files..."
            import plugins.evernote.htmlconvert as en_html 
            en_html.generate_html_files(cfg)
            if cfg['verbose']:
                print "OK, finish :)"
    if not cfg['run_as_service']:
        run = False
