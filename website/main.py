from bottle import route, run, template, static_file

@route('/')
def web_index(name='World'):
    return template('index.tpl', { 'title' : "Mainpage"} )


@route('/config')
def web_config():
    data = { 'cfg' : cfg, 'title' : "Config Overview" }

    return template("config.tpl", data)

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./website/static/')

