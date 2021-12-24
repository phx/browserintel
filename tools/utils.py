import os
import shutil
from pathlib import Path

def is_readable_file(path) -> bool:
	return os.path.isfile(path) and os.access(path, os.R_OK)


def ls(path, files=False, directories=False) -> list:
	paths = [os.path.join(path, f) for f in os.listdir(path) if f]
	rpaths = []
	if files:
		for file in paths:
			if is_readable_file(file):
				rpaths.append(file)
	if directories:
		for directory in paths:
			if os.path.isdir(directory):
				rpaths.append(directory)
	return rpaths


def getfilecount(path) -> int:
	directory = Path(path)
	numfiles = len([name for name in os.listdir(directory) if is_readable_file(os.path.join(directory, name))])
	return numfiles


def getdirsize(path) -> int:
	directory = Path(path)
	sizes = []
	for f in directory.glob('**/*'):
		if not is_readable_file(f):
			continue
		sizes.append(f.stat().st_size)
	bytes = sum(sizes)
	return bytes


def is_installed(required_software: list) -> bool:
	"""
	Checks for required commands from the list provided:
	:param required_software: list
	:return: boolean (or exception)
	"""
	for software in required_software:
		if not shutil.which(software):
			print(f"ERROR: '{software}' is not installed or is not in the $PATH.")
			exit(os.EX_OSERR)
	return True
