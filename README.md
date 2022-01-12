# cPanel Bulk Account Creation
A quick utility script to bulk create cPanel accounts from a csv file.

## Create Accounts
```
usage: create_accounts.py [-h] [--output] [--plan PLAN] [--debug] input

bulk add accounts to cPanel

positional arguments:
  input                 csv file to load input usernames and emails from

optional arguments:
  -h, --help            show this help message and exit
  --output, -o          save csv output for successful and unsuccessful account creations
  --plan PLAN, -p PLAN  the cPanel plan (package) to create the account with
  --debug, -v           print debug messages to the terminal
```
## Fix SSL Certificates
```
usage: fix_ssl.py [-h] [--output] [--redirect] [--debug] input

bulk fix SSL certificates on cPanel accounts

positional arguments:
  input           csv file to load domains from

optional arguments:
  -h, --help      show this help message and exit
  --output, -o    save csv output for successful and unsuccessful SSL certificate fixes
  --redirect, -r  enable http->https redirection on domains
  --debug, -v     print debug messages to the terminal
```
