![Platform: ALL](https://img.shields.io/badge/platform-ALL-green)
![Dependencies: Python3](https://img.shields.io/badge/dependencies-Python3-blue)
![Version: Latest](https://img.shields.io/badge/version-latest-green)
![Follow @rubynorails on Twitter](https://img.shields.io/twitter/follow/rubynorails?label=follow&style=social)

# browserintel

This entire suite of utilities is designed to be run from the `browserintel.py` script, thus it requires a working Python3 environment with native libraries.

Please note that for Chrome encrypted data to be decrypted, you will need to use the `-A` flag and must be running this locally on the host where the data resides (and know the login password in the case of MacOS).

This is not the case for Firefox data, which is unencrypted most of the time, but can be decrypted on a different machine if you know the password it was encrypted with (`-p [MASTER PASSWORD]`).

## Usage

```
usage: browserintel.py [-h] [-u USERNAME] [-p MASTER_PASSWORD] [-b BROWSER_DIR] [-pp PROFILE_DIR] [-cp COOKIES_PATH] [-hp HISTORY_PATH] [-lp LOGINS_PATH] [-A] [-C] [-H] [-L]

Gather data from various browser sqlite databases

optional arguments:
  -h, --help            show this help message and exit

String options:
  -u USERNAME, --user USERNAME
                        set the username for output directory
  -p MASTER_PASSWORD, --masterpass MASTER_PASSWORD
                        master password to use if Mozilla browser data is encrypted
  -b BROWSER_DIR, --browserdir BROWSER_DIR
                        path to main browser directory to search
  -pp PROFILE_DIR, --profile-path PROFILE_DIR
                        path to specific profile directory to search
  -cp COOKIES_PATH, --cookies-path COOKIES_PATH
                        path to cookies database
  -hp HISTORY_PATH, --history-path HISTORY_PATH
                        path to history database
  -lp LOGINS_PATH, --logins-path LOGINS_PATH
                        path to logins database

Boolean options:
  -A, --all             Attempt to gather all data from all installed browsers (except for IE)
  -C, --cookies         attempt to gather cookies information
  -H, --history         attempt to gather history information
  -L, --logins          attempt to gather login information
```

## Important note about AV Detection:

If deployed on a Windows host, the Go binaries may trigger AV in certain cases, so you have been warned.

## Runnng on MacOS:

In order to run on MacOS, you will have to right-click on `tools/hackbrowserdata/hbd-macos`, and Click "Open".

This will actually run it and store results from your local machine probably in your home directory under `results`.

You can then just `rm -rf ~/results`, and run the bash script normally without the binary providing any additional difficulty.

### To-Do:

- [Potentially] add support for additional browsers
- Add local support for more architectures

### Troubleshooting:

For troubleshooting, please submit an issue.
