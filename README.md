# cPanel Management
A set of utility scripts to bulk manage cPanel accounts/domains.

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

## Update SSL Certificates
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

## Check SSL certificate expiry dates
```
usage: ssl_expiry.py [-h] input

Check SSL expiry date on domains in a csv file

positional arguments:
  input       csv file to load domains from

optional arguments:
  -h, --help  show this help message and exit
  ```
