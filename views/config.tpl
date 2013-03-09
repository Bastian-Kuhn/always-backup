%include header title=title

<h1>Configuration</h1>
<h2>Global config</h2>

<form name="config_global">
<input type="hidden" name="element" value="global">
Base Path: <input name="base_path" type="text" size="30" value="{{cfg['global']['base_path']}}"> <br />
<input type="checkbox" name="run_as_service" value="True"{{checkbox(cfg['global']['run_as_service'])}}> Run Backup in loop<br>
<input type="checkbox" name="verbose" value="True" {{checkbox(cfg['global']['verbose'])}}> Verbose Output<br>
<input type="checkbox" name="debug" value="True" {{checkbox(cfg['global']['debug'])}}> Debug Output<br>
<input type="submit" value=" Save global Settings ">
</form>

<h2>Sync Pairs</h2>
%for x in cfg['sync_pairs']:
{{x['source']}} <img src='/static/images/crystal/sync_oneway.png'>  {{x['target']}}
%end

<h2>Webserver Config</h2>
<form name="config_web">
<input type="hidden" name="element" value="webserver">
Bind to IP: <input name="ip" type="text" size="30" value="{{cfg['webserver']['ip']}}"> <br />
Port: <input name="port" type="text" size="30" value="{{cfg['webserver']['port']}}"> <br />
<input type="submit" value=" Save Webserver Settings ">
</form>
%include footer
