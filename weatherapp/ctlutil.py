import socket
from TorCtl import TorCtl
import config

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
    
    def __init__(self,
                 control_host = _CONTROL_HOST,
                 control_port = _CONTROL_PORT,
                 sock = None,
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
            #errormsg = "Could not connect to Tor control port.\n" + \
                       #"Is Tor running on %s with its control port" + \
                       #"opened on %s?" % (control_host, control_port)
            #logging.error(errormsg)
            #print >> sys.stderr, errormsg
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
        C{node_id}.

        @type node_id: str
        @param node_id: Fingerprint of the node requested with no spaces.
        @rtype: str
        @return: String representation of the single descirptor file.
        """
        # get_info method returns a dictionary with single mapping, with
        # all the info stored as the single value, so this extracts the string
        return self.control.get_info("desc/id/" + node_id).values()[0]

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
            # If we're getting here, we're likely seeing:
            # ErrorReply: 552 Unrecognized key "ns/id/46D9..."
            # ^ This was from the original Tor Weather. This probably
            # means simply that a consensus file wasn't found.
            #logging.error("ErrorReply: %s" % str(e))
            return False
        except:
            #logging.error("Unknown exception in ctlutil.is_up()")
            return False

        # If we're here, we were able to fetch information about the router
        return True

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
