from bottle import route, request, run, get, template, static_file

@route('/')
def web_index(name='World'):
    return template('index.tpl', { 'title' : "Mainpage"} )


def set_checkbox(value):
    if value:
        return 'checked="checked"'
    else:
        return ""

@get('/config')
def web_config():
    title = "Config Overview"
    params = dict(request.GET)
    if params.get('element', False):
        title += " (%s - Settings Saved)" % str(params['element'])
        save_config(params)

    data = { 'cfg' : cfg, "request" : params, 'title' : title, 'checkbox' : set_checkbox }

    return template("config.tpl", data)

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./website/static/')

def boolean(value):
    '''Helper function to convert string TRUE/FALSE to python'''
    if value == "True":
        return True
    elif value == "False":
        return  False
    return value

def save_config(data):
    ''' Save the config file and set the config'''
    element = data['element']
    del data['element']
    for key, value in cfg[element].items():
        cfg[element][key] = boolean(data.get(key, False))

    file('local.config','w').write(str(cfg))

