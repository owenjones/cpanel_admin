# SSL Certificate Update Procedure
## Prerequisites
* Python dependencies installed `pip install -r requirements.txt`
* API key (root user, with full privileges) generated and saved in `.env`
* New SSL certificate in PEM format saved in `sslupdate/cert.pem`
* Test set of cPanel accounts (username and domain) saved in `sslupdate/testset.csv`
* Full set of cPanel accounts (username and domain) saved in `sslupdate/fullset.csv`

## Procedure
### 1. Test Certificate Update
1. Run SSL expiry date check on test set: `python ssl_expiry.py sslupdate/testset.csv`
2. Run certificate update on test set: `python update_ssl.py -r -v sslupdate/cert.pem sslupdate/testset.csv`
3. Check update output and confirm successful update
  * If any unsuccessful updates: correct issue and re-run from step 2.
4. Run SSL expiry date check on test set: `python ssl_expiry.py sslupdate/testset.csv`
5. Check new expiry date is shown

### 2. Run Full Certificate Update
1. Run SSL expiry date check on full set: `python ssl_expiry.py sslupdate/fullset.csv`
2. Run certificate update on full set: `python update_ssl.py -r -v sslupdate/cert.pem sslupdate/fullset.csv`
3. Check update output and confirm successful update
4. Run SSL expiry date check on test set: `python ssl_expiry.py sslupdate/fullset.csv`
5. Check new expiry date is shown

### 3. Manually Install Certificate For Root Domain
1. Use the WHM interface to install certificate for root domain (which isn't owned by a cPanel user)

### 4. Clean-up
* Revoke API key

## Known Issues
* To update all domains the API key needs to be created for root with full privileges (this is so it can run API calls on users owned by other resellers)
* Error about `insert_ssl` function being inaccessible - check package list for that user and make sure adding SSL/TLS certificates isn't disabled
