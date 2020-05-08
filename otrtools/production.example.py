#!/usr/bin/python3
import os

ALLOWED_HOSTS = ['example.com']

# Debug = False

# You should use ENV variables instead!
# OTR_USERNAME = "someone@example.com"
# OTR_PASSWORD = "secret password"
# DATENKELLER_USER = "SomeOne123"
# DATENKELLER_PASSWORD = "VeryStrangePass234"

WWW_DIR = '/var/www/html/'

# OTRKEY_CACHE = '/path/to/file'
CUT_DIR = os.path.join(os.environ['HOME'], 'temp')

DEST_DIR = os.path.join(WWW_DIR, 'videos')
DEST_CHOWN_USER, DEST_CHOWN_GROUP = 1000, 1000
DEST_CHMOD = 664
