"""
A module for storing configuration settings.

"""

# XXX: Make bulletproof
authenticator = open("config/auth_token", "r").read().strip()
