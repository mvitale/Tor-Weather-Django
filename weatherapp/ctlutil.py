import socket
from TorCtl import TorCtl
import config

debugfile = open("debug", "w")

class CtlUtil:
    """A class that handles communication with TorCtl"""

    _CONTROL_HOST = "127.0.0.1"
    _CONTROL_PORT = 9051
    _SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _AUTHENTICATOR = config.authenticator
    
    def __init__(self,
                 control_host = _CONTROL_HOST,
                 control_port = _CONTROL_PORT,
                 sock = _SOCK,
                 authenticator = _AUTHENTICATOR):
        self.control_host = control_host
        self.control_port = control_port
        self.sock = sock
        self.authenticator = authenticator

        try:
            self.sock.connect((control_host,control_port))
        except:
            errormsg = "Could not connect to Tor control port" + \
                       "Is Tor running on %s with its control port opened on %s?" \
                       % (control_host, control_port)
            logging.error(errormsg)
            print >> sys.stderr, errormsg
            raise
        self.control = TorCtl.Connection(self.sock)
        self.control.authenticate(config.authenticator)
        self.control.debug(debugfile)

    def ping(self, nodeId):
        """See if this tor node is up by only asking Tor."""
        try:
           info = self.control.get_info(str("ns/id/" + nodeId))
        except TorCtl.ErrorReply, e:
            # If we're getting here, we're likely seeing:
            # ErrorReply: 552 Unrecognized key "ns/id/46D9..."
            # This means that the node isn't recognized by 
            logging.error("ErrorReply: %s" % str(e))
            return False

        except:
            logging.error("Unknown exception in ping()")
            return False

        # If we're here, we were able to fetch information about the router
        return True

    def get_finger_name_list(self):
            #The dictionary returned from TorCtl
            desc_dict = self.connection.get_info("desc/all-recent")

            #A list of the router descriptors in desc_dict
            desc_list = str(descriptor_dict.values()[0]).split("----End Signature----")
            
            #Make a list of tuples of all router fingerprints in descriptor with
            #whitespace removed and router names
            router_list= []

            for desc in desc_list:
                desc_lines = desc.split("\n")
                finger = ""
                for line in desc_lines:
                    if line.startswith("opt fingerprint"):
                        finger = line[15:].replace(' ', '')
                    if line.startswith("router "):
                        split_line = line.split()
                        name = split_line[1]

                #We ignore ORs that don't publish their fingerprints
                if not finger == "":
                    router_list.append((finger, name))
        
        return router_list

    def __del__(self):
        self.sock.close()
        del self.sock
        self.sock = None

        try:
            self.connection.close()
        except:
            pass
        
        del self.control
        self.control = None

