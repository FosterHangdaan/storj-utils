# [storj-utils](https://github.com/FosterHangdaan/storj-utils)
A collection of utilities to help Storj Node Operators (SNOs) manage their storage clusters.

## Requirements
The programs have been tested and are known to run with the following:
- Ubuntu 20.04 (Most likely works in other distros)
- Python 3.8
- BASH 5.0.17

## Installation
To install, just run the installation script within the directory: `sudo ./install.sh`

## Configuration
The first thing that should be done after installation is to add your node information to: _/etc/storj-utils/nodes.json_

As shown below, this file contains the name of your node (the node's container name in docker), the IP address and port of the web UI, and the path to the directory where the docker run script resides.
```json
[
  {
    "name": "xxx",
    "address": "xxx",
    "port": 0,
    "path": "xxx"
  }
]
```

An example of nodes.json containing information for three nodes:
```json
[
  {
    "name": "Node01",
    "address": "localhost",
    "port": 14002,
    "path": "/storj/node01"
  },
  {
    "name": "Node02",
    "address": "localhost",
    "port": 14003,
    "path": "/storj/node02"
  },
  {
    "name": "Node03",
    "address": "127.0.0.1",
    "port": 14004,
    "path": "/storj/node03"
  }
]
```

## Utilities Summary
1. storj-update.sh
  - Updates the Storj docker image. It safely stops all nodes before updating then attempts to restart them.
2. check_storj_update.py
  - A nagios plugin for checking if all Storj nodes are up to date.
3. storj-summary.py
  - Prints a table on the terminal showing essential node statistics such as disk/bandwidth utilization, status, up-to-date status and etc.
4. storjutils.py
  - A python module for storing classes and functions used by the scripts. Currently only contains the StorjNode class for getting node information via its web API.

**Note:** You can automate the Storj Node update process by adding the following to the docker user's cron:
```
* */3 * * * check_storj_update > /dev/null || storj-update > /dev/null
```
This job checks every 3 hours and updates the docker image if an update is available. The path _/usr/local/bin_ should be in the cron PATH environment or provide absolute paths.

## Developer
- [Foster Hangdaan](https://github.com/FosterHangdaan)
