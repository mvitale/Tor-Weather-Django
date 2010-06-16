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
