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

You can unsubscribe from these reports at any time by visiting the 
following url:

%s 

or change your Tor Weather notification preferences here:

%s.
"""

NODE_DOWN_MAIL = """
This is a Tor Weather Report.

It appears that a Tor node you elected to monitor, 

(node id: %s),

has been uncontactable through the Tor network for at least %s.  You may wish
to look at it to see why.  

You can unsubscribe from these reports at any time by visiting the
following url:

%s 

or change your Tor Weather notification preferences here:

%s.
"""

OUT_OF_DATE_MAIL = """
This is a Tor Weather Report.

It appears that a Tor node you elected to monitor,

(node id: %s),

is running an out of date version of Tor. You can download the latest 
version of Tor at %s. 

You can unsubscribe from these reports at any time by visiting the
following url: 

%s

or change your Tor Weather notification preferences here:

%s.
"""

T_SHIRT_MAIL = """
This is a Tor Weather Report.

Congratulations! The node you are observing has been stable for %s,
which makes the operator eligible to receive an official Tor T-shirt!
If you're interested in claiming your shirt, please visit the following
link for more information. 

http://www.torproject.org/tshirt.html

Thank you for your contribution to the Tor network!

You can unsubscribe from these reports at any time by visiting the
following url:

%s

or change your Tor Weather notification preferences here:

%s.
"""

WELCOME_MAIL = """
Hello and welcome to Tor!

We've noticed that your Tor node has been running long enough to be
flagged as "stable". First, we would like to thank you for your 
contribution to the Tor network! As Tor grows, we require ever more 
nodes to optomize browsing speed and reliability for our users. Your 
node is helping to serve the millions of Tor clients out there.

As a node operator, you may be interested in the Tor Weather service,
which sends important email notifications when a node is down or 
your version is out of date. We here at Tor consider this service to
be vitally important and greatly useful to all node operators. If you're 
interested in Tor Weather, please visit the following link to register:
 
https://weather.torproject.org/

You might also be interested in the or-announce mailing list, which is
a low volume list for announcements of new releases and critical 
security updates. To join, send an e-mail message to majordomo@seul.org
with no subject and a body of "subscribe or-announce". 

Thank you again for your contribution to the Tor network! We won't send
you any further emails unless you subscribe.


Disclaimer: If you have no idea why you're receiving this email, we 
sincerely apologize and promise never to email you again!
"""

LEGAL_MAIL = """
Legal mumbo jumbo
"""
