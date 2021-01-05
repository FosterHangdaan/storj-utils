#!/usr/bin/env python3

#Programmer: ........ Foster Hangdaan
#Description: ....... Check to see of STORJ nodes are up to date using
#                     the official STORJ website: storj.io
#Date Released: ..... October 22, 2020
#Version: ........... 1.0

# NOTES:  You can get the "up to date" state of each node
#         by using "curl -s "http://localhost:14002/api/sno/" | jq .upToDate".
#         This can shorten the code siginificantly at the cost of
#         relying on the node itself to report an accurate status.

import requests, json
from storjutils import StorjNode

# NAGIOS Return Codes
#####################
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

if __name__ == '__main__':
    nodes_path = '/etc/storj-utils/nodes.json'
    try:
        with open(nodes_path) as f:
            nodes = json.loads(f.read())
    except FileNotFoundError as fnfe:
        print(fnfe)
        raise SystemExit(STATE_UNKNOWN)

    StorjNodes = []
    for n in nodes:
        StorjNodes.append(StorjNode(n['name'], n['address'], n['port']))

    # Get minimal version from STORJ official website
    current_version = requests.get('https://version.storj.io').json()['processes']['storagenode']['minimum']['version']

    # Get version of the most outdated node
    node_version = sorted([x.get_version() for x in StorjNodes])[0]

    if node_version >= current_version:
        print(f'STORJ Nodes are up to date. Current: {current_version} ; Nodes: {node_version}')
        raise SystemExit(STATE_OK)
    else:
        print(f'STORJ Nodes are OUTDATED. Current: {current_version} ; Nodes: {node_version}')
        raise SystemExit(STATE_CRITICAL)
