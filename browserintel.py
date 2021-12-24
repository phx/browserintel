#!/usr/bin/env python3

import argparse
import os.path

from pathlib import Path
from tools.utils import *
from tools.xplat import Info


# Parse arguments:
parser = argparse.ArgumentParser(add_help=True, description='Gather data from various browser sqlite databases')
string_group = parser.add_argument_group('String options')
string_group.add_argument('-u', '--user', action='store', dest='username', default='user', help='set the username for output directory')
string_group.add_argument('-mp', '--masterpass', action='store', dest='master_password', default=None, help='master password to use if Mozilla browser data is encrypted')
string_group.add_argument('-bn', '--browsername', action='store', dest='browser_name', choices=['chrome', 'firefox', 'palemoon', 'waterfox', 'all'], default='chrome', help="browser to get data from - if 'all' is specified, other unnamed browser data will also be obtained (except for IE)")
string_group.add_argument('-bd', '--browserdir', action='store', dest='browser_dir', default=None, help='path to main browser directory to search')
string_group.add_argument('-p', '--profile', action='store', dest='profile_dir', default=None, help='path to specific profile directory to search')
string_group.add_argument('-cp', '--cookies-path', action='store', dest='cookies_path', default=None, help='path to cookies database')
string_group.add_argument('-hp', '--history-path', action='store', dest='history_path', default=None, help='path to history database')
string_group.add_argument('-lp', '--logins-path', action='store', dest='logins_path', default=None, help='path to logins database')
string_group.add_argument('-P', '--platform', action='store', dest='platform_type', choices=['win32', 'win64', 'linux', 'darwin'], default=None, help='platform type for decrypting local data')
bool_group = parser.add_argument_group('Boolean options')
bool_group.add_argument('-A', '--all', action='store_true', dest='all_true', default=False, help='Attempt to gather all data from all installed browsers (except for IE)')
bool_group.add_argument('-C', '--cookies', action='store_true', dest='cookies_true', default=False, help='attempt to gather cookies information')
bool_group.add_argument('-H', '--history', action='store_true', dest='history_true', default=False, help='attempt to gather history information')
bool_group.add_argument('-L', '--logins', action='store_true', dest='logins_true', default=False, help='attempt to gather login information')
options = parser.parse_args()

info = Info()

if info.platform == 'Darwin':
	if not options.browser_dir and not options.profile_dir:
		chrome_dir = f"/Users/{info.username}/Library/Application Support/Google/Chrome"
		profile_dir = info.get_most_likely_subdir(directory='/Users/phx/Library/Application Support/Google/Chrome')

if profile_dir:
	print(profile_dir)

