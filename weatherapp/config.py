# Tor Weather
# by Jacob Appelbaum <jacob@appelbaum.net>, Christian Fromme <kaner@strace.org>
# Copyright (c) 2009, 2010 The Tor Project
# See LICENSE for licensing information

URLbase = "https://weather.torproject.org"

# XXX: Make bulletproof
authenticator = open("auth_token").read().strip()

mailFrom = "tor-ops@torproject.org"

pollPeriod = 3600 # Check every hour

databaseName = "subscriptions.db"
