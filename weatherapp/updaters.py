import socket
from TorCtl import TorCtl
import config

class CtlConnection:
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

        self.make_connection()

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

    def make_connection(self):
        """Establishes connection with the current instance variables.
        Separated out of __init__ in case we ever want to change a
        CtlConnection object's instance variables and re-establish a connection
        """

        self.sock.connect((self.control_host, self.control_port))
        # TO DO -------------------------------------------------- BASE FEATURE
        # ADD ERROR HANDLING FOR CONNECT --------------------------------------

        self.connection = TorCtl.Connection(self.sock)
        self.connection.authenticate(authenticator)

        return connection

class SubscriptionChecker:
    """A class for checking and updating the various subscription types"""
    
    # TO DO ------------------------------------------------------ BASE FEATURE
    # UPDATE CLASS TO WORK WITH CTLUTIL ---------------------------------------

    def __init__(self):
        self.pinger = TorPing()

    def check_all_down(self):
        """Check if all nodes with node_down subscriptions are up or down, and
        send emails and update subscription data as necessary."""

        #All node down subscriptions
        subscriptions = Subscription.objects.filter(name = "node_down")

        for subscription in subscriptions:
            is_up = self.pinger.ping(subscription.subscriber.router.fingerprint) 
            if is_up:
                if subscription.triggered:
                   subscription.triggered = False
                   subscription.last_changed = datetime.datetime.now()
            else:
                if subscription.triggered:
                    if subscription.should_email():
                        recipient = subscription.subscriber.email
                        Emailer.send_node_down_email(recipient)
                        subscription.emailed = True 
                else:
                    subscription.triggered = True
                    subscription.last_changed = datetime.datetime.now()
        return

    def check_out_of_date():
        # TO DO ------------------------------------------------- EXTRA FEATURE 
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_below_bandwidth():
        # TO DO ------------------------------------------------- EXTRA FEATURE
        # IMPLEMENT THIS ------------------------------------------------------
        pass

    def check_earn_tshirt():
        # TO DO ------------------------------------------------- EXTRA FEATURE
        # IMPLEMENT THIS ------------------------------------------------------
        pass

class RouterUpdater:
    """A class for updating the Router table"""

    # TO DO ------------------------------------------------------ BASE FEATURE
    # UPDATE CLASS TO WORK WITH CTLUTIL ---------------------------------------

    def __init__(self):
        self.connection = CtlConnection()

    def get_finger_print_name_list(self):
        # Make a list of tuples of all router fingerprints in descriptor with
        # whitespace removed and router names
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

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        #The dictionary returned from TorCtl
        desc_dict = self.connection.get_info("desc/all-recent")

        #A list of the router descriptors in desc_dict
        desc_list = str(descriptor_dict.values()[0]).split("----End \
                        Signature----")
        
        for router in router_list:
            is_up = False
            finger = router[0]
            name = router[1]
            try:
                connection.get_info("ns/id/" + finger)
                is_up = True
            except:
                pass
            
            if is_up:
                try:
                    router_data = Router.objects.get(fingerprint = finger)
                    router_data.last_seen = datetime.datetime.now()
                    router_data.name = name
                except DoesNotExist:
                    #let's add it
                    new_router = Router(finger, name, False,
                                        datetime.datetime.now())
        return
