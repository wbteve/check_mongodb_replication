#!/usr/bin/env python
"""
Script to check the replication status of MongoDB in a replica
set. The options for this script are the standard Nagios plugin
options (-w, -c, -H, -t) as well as a --port option for the port
to MongoDB.
"""

import pymongo
import pynagios
from pynagios import Plugin, Response, make_option

class CheckMongoDBReplication(Plugin):
    port  = make_option("--port", help="port to connect to",
                        type="int", default=27017)

    def check(self):
        host = self.options.hostname if self.options.hostname is not None else '127.0.0.1'
        timeout = None if self.options.timeout == 0 else self.options.timeout

        connection = pymongo.connection.Connection(host=host, port=self.options.port,
                                                   network_timeout=timeout)


        # If we're the master, then there is no check to do
        if connection["admin"].command("ismaster")["ismaster"]:
            return Response(pynagios.OK, "Master. Of course we're up to date.")

        status = connection["admin"].command("replGetStatus")
        primary     = None
        this_server = None

        for member in status["members"]:
            if member["stateStr"] == "PRIMARY":
                primary = member
            elif member["self"]:
                this_server = member

        if primary is None:
            return Response(pynagios.CRITICAL, "Primary could not be found in the replica set.")
        elif this_server is None:
            return Response(pynagios.CRITICAL, "This server could not be found in the replica set.")

        difference = primary["optime"]["t"] - this_server["optime"]["t"]
        seconds    = difference / 1000
        return self.response_for_value(seconds, "Replication lag: %d seconds" % seconds)

if __name__ == '__main__':
    CheckMongoDBReplication().check().exit()
