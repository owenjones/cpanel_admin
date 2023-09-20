# cPanel Management
A set of utility scripts to bulk manage cPanel accounts/domains.


## Setup
1. Install Python 3
2. Install virtualenv `python -m pip install virtualenv`
2. Create a new virtual environment `python -m virtualenv .venv`
3. Activate the virtual environment `source .venv/bin/activate` (linux) `.venv\Scripts\activate.bat` (Windows)
4. Install python packages `pip install -r requirements.txt`

## Usage
1. Set server details, username, and API token in `.env` file
2. Setup CSV with user details
3. Call required python script with csv file as input

## CSV file spec
All commands take in a csv file with a header:
* Creating accounts: `username` and `email` fields
* Updating SSL certificates: `username` and `domain` fields

## Command Line Arguments
### Create Accounts
```
usage: create_accounts.py [-h] [--output] [--plan PLAN] [--debug] input

bulk add accounts to cPanel

positional arguments:
  input                 csv file to load input usernames and emails from

optional arguments:
  -h, --help            show this help message and exit
  --plan PLAN, -p PLAN  the cPanel plan (package) to create the account with
  --debug, -v           print debug messages to the terminal
```

### Update SSL Certificates
```
usage: update_ssl.py [-h] [--redirect] [--debug] pem_file accounts_file

bulk update SSL certificates on cPanel accounts

positional arguments:
  pem_file        PEM file to load key and certificate(s) from
  accounts_file   csv file to load accounts from (username and domain required)

optional arguments:
  -h, --help      show this help message and exit
  --redirect, -r  enable http->https redirection on domains
  --debug, -v     print debug messages to the terminal
```

### Check SSL certificate expiry dates
```
usage: ssl_expiry.py [-h] input

Check SSL expiry date on domains in a csv file

positional arguments:
  input       csv file to load domains from

optional arguments:
  -h, --help  show this help message and exit
  ```
