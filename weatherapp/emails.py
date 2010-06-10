#
#
#

CONFIRMATION_MAIL = """
Dear human,

This is the Tor Weather Report system.

Somebody (possibly you) has requested that status monitoring information
about a Tor node (id: %s) be sent to this email address.

If you wish to confirm this request, please visit the following url:

%s

If you do not wish to receive Tor Weather Reports, you do not need to do 
anything.
"""

SUBS_CONFIRMED_MAIL = """
Dear human,

This is the Tor Weather Report system.

You successfully subscribed for weather reports about a tor node.

(node id: %s)

(You can unsubscribe from these reports at any time by visiting the 
following url:

%s)
"""
