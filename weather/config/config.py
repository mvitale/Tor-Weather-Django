"""
The Tor Weather config file.
"""

# XXX: Make bulletproof
authenticator = open("config/auth_token", "r").read().strip()

control_port = 9051
