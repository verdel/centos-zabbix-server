#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests

TG_API_URL = os.getenv('TG_API_URL', sys.argv[1])
TG_API_KEY = os.getenv('TG_API_KEY', sys.argv[2])


class NotifierSender(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def send(self, text):
        r = requests.post(
            url=self.url,
            headers={'Authorization': 'Bearer {}'.format(self.token)},
            data={'message': text},
            verify=False
        )
        self.status_code = r.status_code
        if r.status_code == 401:
            self.status_message = 'Username or password is invalid.'

        elif r.status_code != 200:
            try:
                self.status_message = r.json().error.message

            except:
                self.status_message = r.content
        else:
            self.status_message = r.content

if __name__ == '__main__':
    subject = sys.argv[3]
    text = sys.argv[4]
    r = NotifierSender(
        url=TG_API_URL,
        token=TG_API_KEY
    )
    r.send('{}\r\n{}'.format(subject, text))

    if r.status_code != 200:
        print(r.status_message)
        sys.exit(1)
