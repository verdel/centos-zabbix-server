#!/usr/bin/env python

import subprocess
import time
import os
import argparse
import sys
import socket
from contextlib import closing
import atexit

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'r+b', 0)


class Healthcheck(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _open_socket(self, port):
        try:
            sock = socket.socket()
        except:
            return False
        try:
            sock.bind(('', port))
            sock.listen(1)
        except:
            sock.close()
            return False
        return sock

    def _execute_checks(self):
        methods = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('check_')]
        for method in methods:
            check_result = getattr(self, method)()
            if not check_result:
                return False
        return True

    def run(self):
        sock = None
        while True:
            if self._execute_checks():
                if not sock:
                    sock = self._open_socket(self.healthcheck_port)
                    atexit.register(sock.close)
            else:
                if sock:
                    sock.close()
                    sock = None
            time.sleep(self.healthcheck_interval)


class ZabbixHealthcheck(Healthcheck):
    def check_zabbix_server(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                if sock.connect_ex((self.zabbix_host, int(self.zabbix_port))) == 0:
                    return True
                else:
                    return False
            except:
                return False

    def check_mysql(self):
        try:
            return_code = subprocess.call('mysql -h"{}" -P"{}" -u"{}" -p"{}" --connect-timeout 1 -e "USE {}"'.format(self.mysql_host,
                                                                                                                     self.mysql_port,
                                                                                                                     self.mysql_user,
                                                                                                                     self.mysql_password,
                                                                                                                     self.mysql_db),
                                          stdin=DEVNULL,
                                          stdout=DEVNULL,
                                          stderr=DEVNULL,
                                          shell=True)
        except:
            return False

        if return_code == 0:
            return True
        else:
            return False


def cli():
    parser = argparse.ArgumentParser(description='Zabbix server healthcheck')
    parser.add_argument('--zabbix-host', default=os.environ.get('HEALTHCHECK_ZABBIX_HOST', 'localhost'), help='IP address or dns name of zabbix server', metavar='string')
    parser.add_argument('--zabbix-port', default=os.environ.get('HEALTHCHECK_ZABBIX_PORT', 10051), type=int, help='Port of zabbix server', metavar='int')
    parser.add_argument('--mysql-host', default=os.environ.get('HEALTHCHECK_MYSQL_HOST', 'localhost'), help='IP address of dns name of mysql server', metavar='string')
    parser.add_argument('--mysql-port', default=os.environ.get('HEALTHCHECK_MYSQL_PORT', 3306), type=int, help='Port of mysql server', metavar='int')
    parser.add_argument('--mysql-user', default=os.environ.get('HEALTHCHECK_MYSQL_USER', 'root'), help='Username for mysql server', metavar='string')
    parser.add_argument('--mysql-password', default=os.environ.get('HEALTHCHECK_MYSQL_PASSWORD'), help='Password for mysql server', metavar='string')
    parser.add_argument('--mysql-db', default=os.environ.get('HEALTHCHECK_MYSQL_DB', 'zabbix'), help='Name of mysql database', metavar='string')
    parser.add_argument('--healthcheck-port', default=os.environ.get('HEALTHCHECK_PORT', 5555), type=int, help='TCP port that will be opened in case of a successful check', metavar='int')
    parser.add_argument('--healthcheck-interval', default=os.environ.get('HEALTHCHECK_INTERVAL', 1), type=int, help='Healthcheck interval in seconds', metavar='int')
    return parser.parse_args()


if __name__ == "__main__":
    args = cli()
    check = ZabbixHealthcheck(zabbix_host=args.zabbix_host,
                              zabbix_port=args.zabbix_port,
                              mysql_host=args.mysql_host,
                              mysql_port=args.mysql_port,
                              mysql_user=args.mysql_user,
                              mysql_password=args.mysql_password,
                              mysql_db=args.mysql_db,
                              healthcheck_port=args.healthcheck_port,
                              healthcheck_interval=args.healthcheck_interval)
    check.run()
