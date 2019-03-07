#!/usr/bin/env python3

import getopt
import os
import sys
import json
import varlink

from blkinfo.filters import BlkDiskInfo
from blkinfo.errors import NoLsblkFound

service = varlink.Service(
    vendor='Red Hat',
    product='Blkinfo',
    version='1',
    url='http://varlink.org',
    interface_dir=os.path.dirname(__file__)
)


class ServiceRequestHandler(varlink.RequestHandler):
    service = service


class GetDisksError(varlink.VarlinkError):

    def __init__(self, reason):
        varlink.VarlinkError.__init__(self,
                                      {'error': 'com.redhat.blkinfo.ActionFailed',
                                       'parameters': {'field': reason}})

@service.interface('com.redhat.blkinfo')
class BlkinfoVarlink(object):
    def GetDisksJsonFilters(self, json_filters):

        try:
            blkinfo = BlkDiskInfo()
        except NoLsblkFound as e:
            raise GetDisksError(str(e))

        filters = None
        if json_filters and json_filters != '':
            filters = json.loads(json_filters)

        system_disks = blkinfo.get_disk_list(filters)
        json_output = json.dumps(system_disks)

        return {'json_disks': json_output}


    def StopServing(self, _request=None, _server=None):
        print("Server ends.")

        if _request:
            print("Shutting down client connection")
            _server.shutdown_request(_request)

        if _server:
            print("Shutting down server")
            _server.shutdown()

    def TestObject(self, object):
        return {"object": json.loads(json.dumps(object))}


def run_server(address):
    with varlink.ThreadingServer(address, ServiceRequestHandler) as server:
        print("Listening on", server.server_address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


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

    run_server(address)

    sys.exit(0)
