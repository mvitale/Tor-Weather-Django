"""This module contains the CtlUtil class. CtlUtil objects set up a connection
to TorCtl and handle communication concerning consensus documents and 
descriptor files.

@var debugfile: A log file.
"""

import socket
from TorCtl import TorCtl
import config
import logging
import re
import string

debugfile = open("debug", "w")

class CtlUtil:
    """A class that handles communication with TorCtl.
    
    @type control_host: str
    @ivar control_host: Control host of the TorCtl connection.
    @type control_port: int
    @ivar control_port: Control port of the TorCtl connection.
    @type sock: socket._socketobject
    @ivar sock: Socket of the TorCtl connection.
    @type authenticator: str
    @ivar authenticator: Authenticator string of the TorCtl connection.
    @type control: TorCtl Connection
    @ivar control: Connection to TorCtl.
    """
    _CONTROL_HOST = "127.0.0.1"
    _CONTROL_PORT = 9051
    _AUTHENTICATOR = config.authenticator
    
    def __init__(self, control_host = _CONTROL_HOST, 
                control_port = _CONTROL_PORT, sock = None, 
                authenticator = _AUTHENTICATOR):
                

        self.sock = sock

        if not sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.control_host = control_host
        self.control_port = control_port
        self.authenticator = authenticator

        # Try to connect 
        try:
            self.sock.connect((self.control_host, self.control_port))
        except:
            errormsg = "Could not connect to Tor control port.\n" + \
                       "Is Tor running on %s with its control port" + \
                       "opened on %s?" % (control_host, control_port)
            logging.error(errormsg)
            print >> sys.stderr, errormsg
            raise

        # Create connection to TorCtl
        self.control = TorCtl.Connection(self.sock)

        # Authenticate connection
        self.control.authenticate(config.authenticator)

        # Set up log file
        self.control.debug(debugfile)

    def __del__(self):
        # Probably cleanly closes the connection when the CtlUtil object is 
        # garbage collected. Code taken from original Tor Weather.
        
        self.sock.close()
        del self.sock
        self.sock = None

        try:
            self.connection.close()
        except:
            pass
        
        del self.control
        self.control = None

    def get_single_consensus(self, node_id):
        """Get a consensus document for a specific router with fingerprint
        C{node_id}.

        @type node_id: str
        @param node_id: Fingerprint of the node requested with no spaces.
        @rtype: str
        @return: String representation of the single consensus entry.
        """
        # get_info method returns a dictionary with single mapping, with
        # all the info stored as the single value, so this extracts the string
        return self.control.get_info("ns/id/" + node_id).values()[0]

    def get_full_consensus(self):
        """Get the entire consensus document for every router currently up.

        @rtype: str
        @return: String representation of entire consensus document.
        """
        # get_info method returns a dictionary with single mapping, with
        # all the info stored as the single value, so this extracts the string
        return self.control.get_info("ns/all").values()[0]

    def get_single_descriptor(self, node_id):
        """Get a descriptor file for a specific router with fingerprint 
        C{node_id}. If a descriptor cannot be retrieved, returns the 
        empty string.

        @type node_id: str
        @param node_id: Fingerprint of the node requested with no spaces.
        @rtype: str
        @return: String representation of the single descirptor file or
        the empty string if no such descriptor file exists.
        """
        # get_info method returns a dictionary with single mapping, with
        # all the info stored as the single value, so this extracts the string
        desc = ''
        try:
            desc = self.control.get_info("desc/id/" + node_id).values()[0]
        except TorCtl.ErrorReply, e:
            logging.error("ErrorReply: %s" % str(e))
        except:
            logging.error("Unknown exception in CtlUtil" +
                          "get_single_descriptor()")
        return desc

    def get_full_descriptor(self):
        """Get all current descriptor files for every router currently up.

        @rtype: str
        @return: String representation of all descriptor files.
        """
        # get_info method returns a dictionary with single mapping, with
        # all the info stored as the single value, so this extracts the string
        return self.control.get_info("desc/all-recent").values()[0]

    def get_descriptor_list(self):
        """Get a list of strings of all descriptor files for every router
        currently up.

        @rtype: list[str]
        @return: List of strings representing all individual descriptor files.
        """
        # Individual descriptors are delimited by -----END SIGNATURE-----
        return self.get_full_descriptor().split("-----END SIGNATURE-----")


    def is_up(self, node_id):
        """Check if this node is up (actively running) by requesting a
        consensus document for node C{node_id}. If a document is received
        successfully, then the node is up; if a document is not received, then 
        the router is down. If a node is hiberanating, it will return C{False}.

        @type node_id: str
        @param node_id: Fingerprint of the node in question.
        @rtype: Bool
        @return: Whether the node is up or down.
        """
        try:
           info = self.get_single_consensus(node_id)
        except TorCtl.ErrorReply, e:
            #If we're getting here, we're likely seeing:
            # ErrorReply: 552 Unrecognized key "ns/id/46D9..."
            logging.error("ErrorReply: %s" % str(e))
            return False
        except:
            logging.error("Unknown exception in ctlutil.is_up()")
            return False

        # If we're here, we were able to fetch information about the router
        return True

    def is_exit(self, node_id):
        """Check if this node is an exit node (accepts exits to port 80).
        
        @type node_id: str
        @param node_id: The router's fingerprint
        @rtype: bool
        @return: True if this router accepts exits to port 80, false if not
            or if the descriptor file can't be accessed for this router.
        """
        try:
            descriptor = self.get_single_descriptor(node_id)
            desc_lines = descriptor.split('\n')
            for line in desc_lines:
                if (line.startswith('accept') and (line.endswith(':80') 
                                                   or line.endswith('*:*'))):
                    return True
            return False
        except TorCtl.ErrorReply, e:
            logging.error("ErrorReply: %s" % str(e))
            return False
        except:
            # some other error with the function
            logging.error("Unknown exception in ctlutil.is_exit()")

    def get_finger_name_list(self):
        """Get a list of fingerprint and name pairs for all routers in the
        current descriptor file.

        @rtype: list[(str,str)]
        @return: List of fingerprint and name pairs for all routers in the 
                 current descriptor file.
        """
        # Make a list of tuples of all router fingerprints in descriptor
        # with whitespace removed and router names.
        router_list= []
            
        # Loop through each individual descriptor file.
        for desc in self.get_descriptor_list():
            finger = ""

            # Split each descriptor into lines.
            desc_lines = desc.split("\n")
                
            # Loop through each line in the descriptor.
            for line in desc_lines:
                if line.startswith("opt fingerprint"):
                    # Eliminate 'opt fingerprint' and spaces from line
                    finger = line.replace('opt fingerprint', '')
                    finger = finger.replace(' ', '')
                if line.startswith("router "):
                    # Router name is positioned as second word
                    name = line.split()[1]

            # We ignore routers that don't publish their fingerprints
            if not finger == "":
                router_list.append((finger, name))
        
        return router_list

    def get_finger_list(self):
        """Get a list of fingerprints for all routers in the current
        descriptor file.

        @rtype: list[str]
        @return: List of fingerprints for all routers in the current 
                 descriptor file.
        """
        # Use get_finger_name_list and take out name fields.
        finger_name_list = self.get_finger_name_list()

        finger_list = []
        # Append the first element of each pair.
        for pair in finger_name_list:
            finger_list.append(pair[0])
        
        return finger_list

    def get_bandwidth(single_descriptor):
        """Takes a descriptor for a single router and parses out the 
        bandwidth.
        
        @type single_descriptor: str
        @param single_descriptor: The descriptor for the router
        @rtype: int 
        @return: The router's 'observed' bandwidth, in B/s
        """
        bandwidth = 0
        desc_lines = single_descriptor.split('\n')
        for line in desc_lines:
            if line.startswith('bandwidth'):
                word_list = line.split()
                # the 4th word in the line is the bandwidth-observed in B/s
                bandwidth = int(word_list[3])
        return bandwidth

    def get_new_avg_bandwidth(avg_bandwidth, hours_up, obs_bandwidth):
        """Calculates the new average bandwidth for a router.
        
        @param avg_bandwidth: The current average bandwidth for the router
        @param hours_up: The number of hours this router has been up 
        @param obs_bandwidth: The observed bandwidth taken from the most 
            recent descriptor file for this router
        """
        new_avg = ((hours_up * avg_bandwidth) + obs_bandwidth) / (hours_up + 1)
        return new_avg

    def get_email(self, fingerprint):
        """Get the contact email address for a router operator.

        @type fingerprint: str
        @param fingerprint: The fingerprint of the router whose email will be
                            returned.
        @rtype: str
        @return: The router operator's email address or the empty string if
                the email address is unable to be parsed.
        """
        
        desc = self.get_single_descriptor(fingerprint)
        email = self._parse_email(desc)
        return email

    def is_stable(self, fingerprint):
        """Check if a Tor node has the stable flag.

        @type fingerprint: str
        @param fingerprint: The fingerprint of the router to check

        @rtype: bool
        @return: True if this router has the stable flag, false otherwise.
        """

        info = self.get_single_consensus(fingerprint)
        if re.search('\ns.* Stable ', info):
            return True
        else:
            return False

    def is_hibernating(self, fingerprint):
        """Check if the Tor relay with fingerprint C{fingerprint} is
        hibernating.
        @type fingerprint: str
        @param fingerprint: The fingerprint of the Tor relay to check.

        @rtype: bool
        @return: True if the Tor relay has a current descriptor file with
        the hibernating flag, False otherwise."""

        desc = self.get_single_descriptor(fingerprint)
        if not desc == "":
            hib_search = re.search('opt hibernating 1', desc)
            if not hib_search == None:
                return True
            else:
                return False

    def is_up_or_hibernating(self, fingerprint):
        """Check if the Tor relay with fingerprint C{fingerprint} is up or 
        hibernating.

        @type fingerprint: str
        @param fingerprint: The fingerprint of the Tor relay to check.

        @rtype: bool
        @return: True if self.is_up(fingerprint or 
        self.is_hibernating(fingerprint)."""
        
        return (self.is_up(fingerprint) or self.is_hibernating(fingerprint))

    def _parse_email(self, desc):
        """Parse the email address from an individual router descriptor 
        string.

        @type desc: str
        @param desc: The string representation of the descriptor file for a
                    Tor router.
        @rtype: str
        @return: The email address in desc. If the email address cannot be
                parsed, the empty string.
        """
        split_desc = desc.split('\n')
        contacts = []
        punct = string.punctuation
        for line in split_desc:
            if line.startswith('contact '):
                contacts.append(line)
        for line in contacts:
            clean_line = line.replace('<', ' ').replace('>', ' ') 
            email = re.search('[^ <]*@.*\.[^\n \)\(>]*', clean_line)
            if email == None:
                email = re.search('[^\s]*\s(?:@|at|['+punct+']*at['+punct+']*' +
                ')\s.*\s(?:\.|dot|d0t|['+punct+']*dot['+punct+']*)\s[^\n\)\(]*',
                clean_line, re.IGNORECASE)
                if email == None:
                    email = re.search('[^\s]*\s(?:@|at|['+punct+']*at['+punct+
                                    ']*)\s.*\.[^\n\)\(]*', clean_line, 
                                                                re.IGNORECASE)
        if email == None:
            #----Learn how logging works and configure!------
            #errormsg = ('Could not parse the following contact line:\n'+ line)
            #logging.error(errormsg)
            #print >> sys.stderr, errormsg
            email = ""
        else:
            email = email.group()
        return email
