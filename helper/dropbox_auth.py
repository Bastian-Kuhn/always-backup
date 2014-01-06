#!/usr/bin/python
import sys
sys.path.insert(0, '../api')
import dropbox
from base64 import b64encode, b64decode


def decode_key(key):
    key, secret = key.split('|')
    key = b64decode(key)
    key = [ord(x) for x in key]
    secret = b64decode(secret)

    s = range(256)
    y = 0
    for x in xrange(256):
        y = (y + s[len(key)] + key[x % len(key)]) % 256
        s[x], s[y] = s[y], s[x]

    x = y = 0
    result = []
    for z in range(len(secret)):
        x = (x + 1) % 256
        y = (y + s[x]) % 256
        s[x], s[y] = s[y], s[x]
        k = s[(s[x] + s[y]) % 256]
        result.append(chr((k ^ ord(secret[z])) % 256))

    key = ''.join([chr(a) for a in key])
    return ''.join(result).split('?', 2)

# I dont understand the idea to conceal the keys and decode it directly after...
# in fact, i think thats stupid but what can i do...
app_key, app_secret = decode_key("N6bIhPubg6A=|NUYVEbxJTEMZr5hxYsGbhAWuVqEpujqkmuCyv6MJ3A==")

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# Have the user sign in and authorize this token
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
access_token, user_id = flow.finish(code)


print "'auth_token': '%s'" % access_token

