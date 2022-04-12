import os
import csv
import asyncio

import aiohttp
import pem

from whmapi import WHMAPI


def load_accounts(file: str) -> list[dict]:
    accounts = []

    with open(file) as input:
        rows = csv.DictReader(input)
        for row in rows:
            accounts.append({"username": row["username"], "domain": row["domain"]})

    return accounts


def load_certificate(file: str) -> dict:
    p = pem.parse_file(file)
    return {"key": p[0], "certificate": p[1], "chain": p[2:]}


async def fix_ssl(
    api: WHMAPI,
    domains: list[dict],
    crt: str,
    key: str,
    cab: str,
    redirect: bool,
    successful: list,
    unsuccessful: list,
):
    # bit of a mess of nested API calls here...

    async with aiohttp.ClientSession() as session:
        for domain in domains:
            try:
                async with api.remove_certificate(session, domain) as response:
                    status = await response.json(content_type="text/plain")

                    if "metadata" in status and status["metadata"]["result"] == 1:
                        async with api.add_certificate(
                            session, domain, crt, key, cab
                        ) as response:
                            status = await response.json(content_type="text/plain")

                            if status["data"]["uapi"]["status"] == 1:
                                if redirect:
                                    async with api.redirect_https(
                                        session, domain
                                    ) as response:
                                        status = await response.json(
                                            content_type="text/plain"
                                        )

                                successful.append(domain)
                            else:
                                unsuccessful.append(
                                    (
                                        domain["domain"],
                                        status["data"]["uapi"]["errors"],
                                    )
                                )
                    else:
                        unsuccessful.append((domain["domain"], status))

            except Exception as e:
                unsuccessful.append((domain, e))


if __name__ == "__main__":
    import time

    from dotenv import load_dotenv
    from argparse import ArgumentParser

    load_dotenv()

    parser = ArgumentParser(
        description="bulk update SSL certificates on cPanel accounts"
    )
    parser.add_argument(
        "pem_file", type=str, help="PEM file to load key and certificate(s) from"
    )
    parser.add_argument(
        "accounts_file",
        type=str,
        help="csv file to load accounts from (username and domain required)",
    )
    parser.add_argument(
        "--redirect",
        "-r",
        action="store_true",
        help="enable http->https redirection on domains",
    )
    parser.add_argument(
        "--debug",
        "-v",
        action="store_true",
        help="print debug messages to the terminal",
    )
    args = parser.parse_args()

    def debug(message: str):
        if args.debug:
            print(message)

    api = WHMAPI(
        os.getenv("WHMSERVER", "127.0.0.1"),
        os.getenv("WHMPORT", 2087),
        os.getenv("WHMUSER"),
        os.getenv("WHMTOKEN"),
    )

    domains = load_accounts(args.accounts_file)
    p = load_certificate(args.pem_file)
    chain = "".join(list(map(str, p["chain"])))

    successful = []
    unsuccessful = []

    asyncio.run(
        fix_ssl(
            api,
            domains,
            str(p["certificate"]),
            str(p["key"]),
            chain,
            args.redirect,
            successful,
            unsuccessful,
        )
    )

    debug(f"Run finished: { len(successful) } SSL certificates fixed.")

    if len(unsuccessful) > 0 and args.debug:
        debug(
            f"There was a problem fixing SSL certificates for { len(unsuccessful) } domains(s):\n"
        )

        for domain, error in unsuccessful:
            debug(f"{ domain } - { error }")

    if not os.path.exists("output"):
        os.makedirs("output")

    t = int(time.time())
    with open(f"output/update_{t}_successful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["domain"])
        for domain in successful:
            writer.writerow([domain["domain"]])

    with open(f"output/update_{t}_unsuccessful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["domain", "error"])
        for domain, error in unsuccessful:
            writer.writerow([domain, error])
