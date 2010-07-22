"""
Configuration settings.

@var authenticator: The authentication key
@var listener_port: The Tor control port for the listener to use. This port
    must be configured in the torrc file.
@var updater_port: The Tor control port for the updater to use. This port 
    must be configured in the torrc file.
@var base_url: The root URL for the Tor Weather web application.
"""

# XXX: Make bulletproof
authenticator = open("config/auth_token", "r").read().strip()

#The Tor control port for listener to use. Must be configured in your torrc file
listener_port = 9051

#The Tor control port for updaters to use. Must be configured in your torrc file
updater_port = 9051

#The base URL for the Tor Weather web application:
base_url = 'http://www.weather.torproject.org'
