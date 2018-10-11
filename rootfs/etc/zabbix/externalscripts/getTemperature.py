#!/usr/bin/python

import sys
import urllib2
import json
import base64

username = 'verdel'
password = 'Pa$$word'

req = urllib2.Request("http://10.15.4.200/api/temperature", None)
req.add_header('Authorization', b'Basic ' + base64.b64encode(username + b':' + password))

opener = urllib2.build_opener()
f = opener.open(req)

obj = json.load(f)
temperature = obj['Value']
print temperature
