import getpass
import pwd
import platform

from tools.utils import *

class Platform:
	def __init__(self):
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

	def get_browser_dir(self, platform=None, user=None, browser_name=None) -> str:
		if not platform:
			platform = self.platform
		if not user:
			user = self.username
		if platform == 'Windows':
			if not browser_name or browser_name == 'chrome':
				chrome_dir = f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/Default"
				if os.path.isdir(chrome_dir):
					return chrome_dir
		elif platform == 'Darwin':
			if not browser_name or browser_name == 'chrome':
				chrome_dir = f"/Users/{user}/Library/Application Support/Google/Chrome/Default"
				if os.path.isdir(chrome_dir):
					return chrome_dir
		elif platform == 'Linux':
			if not browser_name or browser_name == 'chrome':
				chrome_dir = f"/home/{user}/.config/google-chrome/default"
				if os.path.isdir(chrome_dir):
					return chrome_dir
		else:
			return None

