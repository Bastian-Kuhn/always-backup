#!/usr/bin/python

from config import *
try:
    from config_bk import *
except:
    pass

from bk_evernote import evernote_get_local_notes, evernote_clean_filename

evernote_basepath = cfg_backup_base_url + "/evernote/notebooks"
""" Very very simple html creater for notes """
def evernote_generate_html_files():
    index = file(evernote_basepath + "/index.html", 'w')
    index.write("""
        <html>
         <head>
           <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=utf-8">
          </head>
         <body>
         <ul>
        """)
    for notebook, notes in evernote_get_local_notes().items(): 
        notebook_path = evernote_basepath + "/" + notebook
        index.write("<li><a href='%s'>%s</a> <ul>" % (notebook_path, notebook))
        for note in notes:
            note_path = notebook_path + "/" + evernote_clean_filename(note[1]['title'])
            note_content = file(note_path).read()
            output = file(note_path + ".html", 'w')
            output.write("""
                     <html>
                      <head>
                       <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=utf-8">
                      </head>
                      <body>
                        %s
                      </body>
                     </html>
                     """ % note_content)
            output.close()
            index.write("<li><a href='%s'>%s</a></li>" % (note_path + ".html", note[1]['title']))
        index.write("</ul>")
    index.write("</ul></body></html>")
    index.close()




