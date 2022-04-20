import os
import csv
import ssl
from datetime import datetime

import OpenSSL


def load_domains(file: str) -> list[str]:
    domains = []

    with open(file) as input:
        rows = csv.DictReader(input)
        for row in rows:
            domains.append(row["domain"])

    return domains


def get_SSL_expiry_date(domain: str) -> datetime:
    c = ssl.get_server_certificate((domain, 443))
    x = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, c)
    d = x.get_notAfter()
    return datetime.strptime(str(d), "b'%Y%m%d%H%M%SZ'")


if __name__ == "__main__":
    import time
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Check SSL expiry date on domains in a csv file"
    )
    parser.add_argument("input", type=str, help="csv file to load domains from")
    args = parser.parse_args()

    if not os.path.exists("output"):
        os.makedirs("output")

    domains = load_domains(args.input)
    dates = map(get_SSL_expiry_date, domains)
    expiry = dict(zip(domains, dates))

    t = int(time.time())
    with open(f"output/{t}_sslexpiry.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["domain", "expires"])
        for domain, expires in expiry.items():
            writer.writerow([domain, expires.strftime("%d %B %Y, %H:%M")])
