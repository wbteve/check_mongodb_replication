# check_mongodb_replication

This is a Nagios script that will check that Nagios replication
for a replica set does not fall too far behind. The requirements
for the script is in the `requirements.txt`. The script itself
is a standard Nagios check script that accepts parameters such as
`-w`, `-c`, `-H`, `-t`, etc.
