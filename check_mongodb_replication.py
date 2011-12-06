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
                                                   network_timeout=timeout, slave_okay=True)

        status = connection["admin"].command("replSetGetStatus")
        primary     = None
        this_server = None

        for member in status["members"]:
            if member["stateStr"] == "PRIMARY":
                primary = member
            if "self" in member and member["self"]:
                this_server = member

        if primary is None:
            return Response(pynagios.CRITICAL, "Primary could not be found in the replica set.")
        elif this_server is None:
            return Response(pynagios.CRITICAL, "This server could not be found in the replica set.")
        elif primary["name"] == this_server["name"]:
            return Response(pynagios.OK, "Master. Of course we're up to date.")

        # Determine the lag time in seconds. Sometimes this is less than 0
        # which we can just assume to mean 0 (up to date).
        seconds = primary["optime"].time - this_server["optime"].time
        if seconds < 0: seconds = 0
        return self.response_for_value(seconds, "Replication lag: %d seconds" % seconds)

if __name__ == '__main__':
    CheckMongoDBReplication().check().exit()
