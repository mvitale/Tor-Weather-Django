"""
A module for storing configuration settings.

"""

# XXX: Make bulletproof
authenticator = open("config/auth_token", "r").read().strip()

#The Tor control port for listener to use. Must be configured in your torrc file
listener_port = '9055'
