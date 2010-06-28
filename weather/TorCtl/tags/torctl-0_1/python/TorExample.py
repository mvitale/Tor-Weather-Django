#!/usr/bin/python
# TorExample.py -- Python module to demonstrate tor controller functionality.
# Copyright 2005 Nick Mathewson -- See LICENSE for licensing information.
#$Id: TorExample.py 6847 2005-07-17 23:08:42Z arma $

import socket
import sys
from TorCtl import *

"""
Tor Control Client Example
A very basic demonstration of using the TorCtl module to communicate and control
a Tor server.

Usage:
  TorExample.py <parameters> <command list>

Parameters:
  --host <hostname>:<port#>  defaults to "localhost:9100"
  --verbose | -v             turn on verbose messages
  
Commands:
  set_config <config key>=<config value> [<config key>=<config value> ...]
  get_config <config key> [<config key> ...]
  get_info   <info key> [<info key> ...]
  listen     <event name>
  signal     <signal name>
  auth_demo  <auth token>
  
For example, to listen for any error messages do:

  python TorExample listen ERR
"""

def getConnection(daemon=1):
    """
    getConnection tries to open a socket to the tor server.
    If a socket is established, and the daemon paramter is True (the default),
    a thread is spawned to handle the communcation between us and the tor server.
    """
    hostport = "localhost:9100"
    verbose = 0
    while sys.argv[1][0] == '-':
        if sys.argv[1] == '--host':
            hostport = sys.argv[2]
            del sys.argv[1:3]
        elif sys.argv[1].startswith("--host="):
            hostport = sys.argv[1][7:]
            del sys.argv[1]
        elif sys.argv[1] in ('-v', '--verbose'):
            verbose = 1
            del sys.argv[1]

    host,port = parseHostAndPort(hostport)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,port))
    except socket.error, e:
        print "Connection failed: %s. Is the ControlPort enabled?"%e
        sys.exit(1)
    conn = get_connection(s)
    if verbose and hasattr(conn, "debug"):
        conn.debug(sys.stdout)
    th = conn.launch_thread(daemon)
    conn.authenticate("")
    return conn

def run():
    """
    Locate the member function named on the command line and call it.
    The function is located by pre-pending 'run_' to the parameter
    and looking for that named item in the python globals() list.
    """
    if len(sys.argv)<2:
        print "No command given. Finished."
        return
    cmd = sys.argv[1].replace("-","_")
    del sys.argv[1]
    fn = globals().get("run_"+cmd)
    if fn is None:
        print "Unrecognized command:",cmd
        return
    try:
        fn()
    except ErrorReply, e:
        print "Request failed: %s"%e

def run_set_config():
    """
    walk thru the config key=value pairs present on the command line
    and pass them to the tor server.  If the --save option is present,
    tell the tor server to flush the config to disk
    """
    conn = getConnection()
    if sys.argv[1] == '--save':
        save = 1
        del sys.argv[1]
    else:
        save = 0
    kvList = []
    for i in xrange(1, len(sys.argv), 2):
        kvList.append((sys.argv[i], sys.argv[i+1]))
    conn.set_options(kvList)
    if save:
        conn.save_conf()

def run_get_config():
    """
    pass the given configuration key names to the tor server and receive their current values
    """
    conn = getConnection()
    opts = conn.get_option(sys.argv[1:])
    for k,v in opts:
        print "KEY:",k
        print "VALUE:",v

def run_get_info():
    """
    pass the given info key names to the tor server and receive their current values
    """
    conn = getConnection()
    opts = conn.get_info(sys.argv[1:])
    for k in sys.argv[1:]:
        print "KEY:",k
        print "VALUE:",opts.get(k)

def run_listen():
    """
    pass to the tor server the given event name to listen for
    NOTE: after this command the example client will just loop
    and print any passed event items - you will have to kill it
    in order to stop it
    """
    conn = getConnection(daemon=0)
    events = []
    conn.set_event_handler(DebugEventHandler())
    conn.set_events(sys.argv[1:])

def run_signal():
    """
    pass to the tor server the given signal
    """
    conn = getConnection()
    if len(sys.argv)<2:
        print "Syntax: signal [signal]"
        return
    conn.send_signal(sys.argv[1])

def run_authdemo():
    """
    connect to the tor server and authenticate
    """
    conn = getConnection()
    conn.close()
    #XXXX

if __name__ == '__main__':
    run()

