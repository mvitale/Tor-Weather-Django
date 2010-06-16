import socket
from TorCtl import TorCtl
import ctlutil
import config


class RouterUpdater:
    """A class for updating the Router table and sending 'welcome' emails"""

    def __init__(self):
        self.ctl_util = ctlutil.CtlUtil()

    def update_all(self):
        """Add ORs we haven't seen before to the database and update the
        information of ORs that are already in the database."""

        finger_name = ctl_util.get_finger_name_list()

        for router in finger_name:

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
            finger = router[0]
            name = router[1]
            is_up = ctl_util.ping(finger)

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
