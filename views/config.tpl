%include header

<h1>Configuration</h1>
<h2>Global config</h2>
{{cfg['global']}}
<h2>Sync Pairs</h2>
%for x in cfg['sync_pairs']:
{{x['source']}} <img src='/static/images/crystal/sync_oneway.png'>  {{x['target']}}
%end
<h2>Webserver Config</h2>
{{cfg['webserver']}}
%include footer
