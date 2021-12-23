# browserintel

**Dependencies:**

- Bash (not `sh`)
- Python3

This entire suite of utilities is designed to be run from the `browserintel.sh` bash script, thus it requires Linux or MacOS (it is untested with Cygwin or Git-bash).

I am probably going to rewrite this in Python3 so that it will be cross-compatible on Windows, because there are a few aspects where it could prove very useful when run on a Windows host.

Please note that for Chrome encrypted data to be decrypted, you will need to be running this locally on the host where the data resides and know the password.

This is not the case for Firefox encrypted data, which can be decrypted remotely.

I am not going to fully-document everything yet until this is complete, but I will simply provide the usage output for now:

```
Usage: ./browserintel.sh <-P [platform]> <-u [username]> <-b [browser]> [options]
Options (strings):
  -u | --user		username	[-u username] (optional)				Default: user
  -p | --pass		password to decrypt any encrypted data [-p password] (optional)		Default: [None]
  -b | --browser	browser name	[-b chrome|firefox|palemoon|waterfox] (optional) 	Default: chrome
  -B | --browser-dir	browser dir	[-B /path/to/browser_dir] (not necessary for -h, -l, or -c)
  -S | --profile	specific profile (if -S is specified, that profile will be used. Automatically detected with '-B')
  -P | --platform	platform type	[-P win32|win64|linux|darwin] (optional - requires -L)	Default: [None]
  -f | --history	history file	[-h '/path/to/history_db']
  -l | --logindata	login data file	[-l '/path/to/logindata_db']
  -c | --cookies	cookies file	[-c '/path/to/cookies_db']
  -h | --help		display this help text and exit

Options (boolean):
  -A | --all		get local data from all browsers (requires -L and -P)			Default: False
  -C | --cookies-true	get cookies	[-B '/path/to/browser_dir' -C]				Default: False
  -D | --logindata-true get login data	[-B '/path/to/browser_dir' -L]				Default: False
  -H | --history-true	get history	[-B '/path/to/browser_dir' -H]				Default: False
  -L | --local		get data from localhost (requires authentication) [-P platform -L]	Default: False
```

## Important note about AV Detection:

If deployed on a Windows host, the Go binaries may trigger AV, so you have been warned.

## Runnng on MacOS:

In order to run on MacOS, you will have to right-click on `tools/hackbrowserdata/hbd-macos`, and Click "Open".

This will actually run it and store results from your local machine probably in your home directory under `results`.

You can then just `rm -rf ~/results`, and run the bash script normally without the binary providing any additional difficulty.

### Troubleshooting

For troubleshooting, please submit an issue.
