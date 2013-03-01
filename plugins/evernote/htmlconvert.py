#!/usr/bin/python
import evernote_tools as et

""" Very very simple html creater for notes """
def generate_html_files(cfg):
    evernote_basepath = cfg['backup_target'] + "/evernote/notebooks"
    index = file(evernote_basepath + "/index.html", 'w')
    index.write("""
        <html>
         <head>
           <META HTTP-EQUIV="content-type" CONTENT="text/html; charset=utf-8">
          </head>
         <body>
         <ul>
        """)
    for notebook, notes in et.get_local_notes(evernote_basepath).items(): 
        notebook_path = evernote_basepath + "/" + notebook
        index.write("<li><a href='%s'>%s</a> <ul>" % (notebook_path, notebook))
        for note in notes:
            note_path = notebook_path + "/" + et.clean_filename(note[1]['title'])
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




