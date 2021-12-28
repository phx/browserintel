import os
import platform

# Check for Python >=3.6:
target_version = 3.6
python_version = float(platform.python_version()[0:3])

if python_version < target_version:
	print('This script requires Python >=' + str(self.target_version))
	sys.exit(os.EX_SOFTWARE)