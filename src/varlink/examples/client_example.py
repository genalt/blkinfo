#!/usr/bin/env python3

import getopt
import sys
import json

from sys import platform

from builtins import int
from builtins import next
from builtins import object
from builtins import range

import varlink


def run_client(address):
    client = varlink.Client.new_with_address(address)
    print('Connecting to %s\n' % client)

    try:
        with client.open('com.redhat.blkinfo', namespaced=True) as con:
            filters = {
                'min_size': 200
            }

            fields = ['serial', 'name', 'model']

            ret = con.GetDisksJsonFilters(json.dumps(filters), fields)
            print(ret.blk_devices)
    except varlink.ConnectionError as e:
        print("ConnectionError:", e)
        raise e
    except varlink.VarlinkError as e:
        print(e)
        print(e.error())
        print(e.parameters())
        raise e

def usage():
    print('Usage: %s --varlink=<unix socket path>' % sys.argv[0], file=sys.stderr)
    print('\tSelf Exec: $ %s' % sys.argv[0], file=sys.stderr)
    print('\tServer   : $ %s --varlink=<unix socket path>' % sys.argv[0], file=sys.stderr)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hv:', ["help", "varlink="])
    except getopt.GetoptError:
        print("1")
        usage()
        sys.exit(2)

    address = None

    for opt, arg in opts:
        if opt == "--help":
            usage()
            sys.exit(0)
        elif opt == "--varlink":
            address = arg

    if not address:
        usage()
        sys.exit(2)

    run_client(address)
    sys.exit(0)

