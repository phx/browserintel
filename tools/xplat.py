import getpass
import pwd
import platform
import struct

from tools.utils import *


class Platform:
	def __init__(self):
		self.arch = struct.calcsize("P") * 8
		self.name = os.name
		self.platform = platform.system() # Linux, Darwin, or Windows
		self.release = platform.release()


class Info(Platform):
	def __init__(self):
		super().__init__()
		self.uid = os.getuid()
		self.username = getpass.getuser()
		self.username_alt = pwd.getpwuid(os.getuid()).pw_name
		self.home = self.get_user_home_dir()

	def get_user_home_dir(self, user=None):
		if not user:
			user = self.username
		if self.platform == 'Linux':
			if user == 'root':
				return '/root'
			return f"/home/{user}"
		elif self.platform == 'Darwin':
			return f"/Users/{user}"
		elif self.platform == 'Windows':
			return f"C:/Users/{user}"
		return None

	def get_appdata_dir(self, platform=None, user=None, roaming=False, local=False, locallow=False, escaped=False) -> str:
		if not platform:
			platform = self.platform
		if not user:
			user = self.username
		if platform == 'Darwin':
			appdata = f"/Users/{user}/Library/Application Support"
			if escaped:
				return appdata.replace(' ', '\\ ')
			return appdata
		if platform == 'Windows':
			if not local and not locallow:
				return os.getenv('APPDATA')
			elif local:
				return os.getenv('LOCALAPPDATA')
			elif locallow:
				return f"{os.getenv('APPDATA')}\..\LocalLow"
		if platform == 'Linux':
			return f"/home/{user}/.config"
		return None

	def get_most_likely_subdir(self, directory=None, directories=None) -> str:
		if directory:
			directories = ls(directory, directories=True)
			target_dir = self.get_most_likely_subdir(directories=directories)
			return target_dir
		prev = 0
		for directory in directories:
			numfiles = len(ls(directory, directories=True))
			if not numfiles > prev:
				continue
			prev = numfiles
			target_dir = directory
		return target_dir

	@staticmethod
	def get_existing_paths(paths: list) -> list:
		paths = [path for path in paths if path]
		existing_paths = []
		for path in paths:
			if os.path.exists(path):
				existing_paths.append(path)
		return existing_paths

	def get_profiles(self, directories=None, is_profile=None, automatic=False, chrome=False, mozilla=False, most_likely=False, getlist=False):
		if automatic:
			directories = self.get_browser(listbrowsers=True)
		if most_likely:
			return self.get_most_likely_subdir(directories=directories)    # str
		chrome_profiles = []
		mozilla_profiles = []
		profiles = {}
		profile_list = []
		for directory in directories:
			if is_profile:
				profile = directory
			else:
				profile = self.get_most_likely_subdir(directory)
			# Check if chrome:
			if os.path.isfile(f"{profile}/Cookies"):
				chrome_profiles.append(profile)
				profile_list.append(profile)
			# Check if mozilla:
			if os.path.isfile(f"{profile}/cookies.sqlite"):
				mozilla_profiles.append(profile)
				profile_list.append(profile)
		if getlist:
			return profile_list         # list
		if chrome and not mozilla:
			return chrome_profiles      # list
		if mozilla and not chrome:
			return mozilla_profiles     # list
		profiles['chrome'] = {}
		profiles['mozilla'] = {}
		profiles['chrome'] = chrome_profiles
		profiles['mozilla'] = mozilla_profiles
		return profiles                 # dict

	def get_browser(self, platform=None, user=None, browser_name=None, listbrowsers=False, getprofile=False, most_likely=False):
		if not platform:
			platform = self.platform
		if not user:
			user = self.username
		if platform == 'Windows':
			if not browser_name:
				roaming = f"C:/Users/{user}/AppData/Roaming"
				local_appdata = f"C:/Users/{user}/AppData/Local"
				default_chrome_dir = f"{local_appdata}/Google/Chrome/User Data"
				default_chromebeta_dir = f"{local_appdata}/Google/Chrome Beta/User Data"
				default_chromecanary_dir = f"{local_appdata}/Google/Chrome SxS/User Data"
				default_chromedev_dir = None
				default_chromium_dir = f"{local_appdata}/Chromium/User Data"
				default_firefox_dir = f"{roaming}/Mozilla/Firefox/Profiles"
		elif platform == 'Darwin':
			if not browser_name:
				application_support = f"/Users/{user}/Library/Application Support"
				default_chrome_dir = f"{application_support}/Google/Chrome"
				default_chromebeta_dir = f"{application_support}/Google/Chrome Beta"
				default_chromedev_dir = None
				default_chromecanary_dir = f"{application_support}/Google/Chrome Canary"
				default_chromium_dir = f"{application_support}/Chromium"
				default_firefox_dir = f"{application_support}/Firefox/Profiles"
		elif platform == 'Linux':
			if not browser_name:
				if os.getenv('CHROME_CONFIG_HOME'):
					config_dir = os.getenv('CHROME_CONFIG_HOME')
				elif os.getenv('XDG_CONFIG_HOME'):
					config_dir = os.getenv('XDG_CONFIG_HOME')
				else:
					config_dir = f"/home/{user}/.config"
				default_chrome_dir = f"{config_dir}/google-chrome"
				default_chromebeta_dir = f"{config_dir}/google-chrome-beta"
				default_chromecanary_dir = None
				default_chromedev_dir = f"{config_dir}/google-chrome-unstable"
				default_chromium_dir = f"{config_dir}/chromium"
				default_firefox_dir = f"/home/{user}/.mozilla/firefox"
		else:
			return None
		directories = [
			default_chrome_dir, default_chromebeta_dir, default_chromedev_dir, default_chromecanary_dir,
		    default_chromium_dir, default_firefox_dir
		]
		browser_dict = {
			'chrome': {'default_chrome_dir': default_chrome_dir,
			           'default_chromebeta_dir': default_chromebeta_dir,
			           'default_chromedev_dir': default_chromedev_dir,
			           'default_chromecanary_dir': default_chromecanary_dir,
			           'defaultdefault_chromium_dir': default_chromium_dir},
			'mozilla': {'default_firefox_dir': default_firefox_dir}
		}
		for k, v in browser_dict.items():
			for _, i in v.items():
				if not i:
					del v
		print(browser_dict)
		existing_browser_paths = self.get_existing_paths(directories)
		if listbrowsers:
			return existing_browser_paths   # list
		if getprofile:
			return self.get_profile_dirs(directories=self.get_existing_paths(directories))  # str
		if most_likely:
			return self.get_most_likely_subdir(directories=existing_browser_paths)  # str
		return browser_dict # dict

