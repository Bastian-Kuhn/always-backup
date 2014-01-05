#!/usr/bin/python
import sys
sys.path.insert(0, '../api')
import dropbox

app_key = raw_input("1. Enter APP Key: ").strip()
app_secret = raw_input("2. Enter APP Secret: ").strip()

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# Have the user sign in and authorize this token
authorize_url = flow.start()
print '3. Go to: ' + authorize_url
print '4. Click "Allow" (you might have to log in first)'
print '5. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
access_token, user_id = flow.finish(code)


print "{'auth_token': '%s', 'app_secret': '%s', 'app_key': '%s'}" % \
  (access_token, app_secret, app_key)

