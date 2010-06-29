# Tor Weather
# by Jacob Appelbaum <jacob@appelbaum.net>, Christian Fromme <kaner@strace.org>
# Copyright (c) 2009, 2010 The Tor Project
# See LICENSE for licensing information

URLbase = "127.0.0.1:8000"

# XXX: Make bulletproof
authenticator = open("config/auth_token", "r").read().strip()

mailFrom = "tor-ops@torproject.org"
