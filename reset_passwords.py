import csv
import asyncio

import aiohttp

from whmapi import Account, WHMAPI


def load_accounts(file: str) -> list[Account]:
    accounts = []

    with open(file) as input:
        rows = csv.DictReader(input)
        for row in rows:
            accounts.append(Account(row["username"], ""))

    return accounts


async def reset_passwords(
    api: WHMAPI,
    accounts: list[Account],
    successful: list,
    unsuccessful: list,
):
    async with aiohttp.ClientSession() as session:
        for account in accounts:
            try:
                async with api.reset_password(session, account) as response:
                    status = await response.json(content_type="text/plain")

                    if status["metadata"]["result"] == 1:
                        successful.append(account)
                    else:
                        unsuccessful.append((account, status["metadata"]["reason"]))

            except Exception as e:
                unsuccessful.append((account, e))


if __name__ == "__main__":
    import os
    import time

    from dotenv import load_dotenv
    from argparse import ArgumentParser

    load_dotenv()

    parser = ArgumentParser(description="bulk reset cPanel account passwords")
    parser.add_argument(
        "input", type=str, help="csv file to load input usernames from"
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

    if not os.path.exists("output"):
        os.makedirs("output")

    accounts = load_accounts(args.input)
    successful = []
    unsuccessful = []
    asyncio.run(reset_passwords(api, accounts, successful, unsuccessful))

    debug(
        f"Run finished: { len(successful) } passwords reset."
    )

    if len(unsuccessful) > 0 and args.debug:
        debug(f"There was a problem resetting the password for { len(unsuccessful) } account(s):\n")
        for account, error in unsuccessful:
            debug(f"{ account.username } - { error }")

    t = int(time.time())
    with open(f"output/{t}_reset_password_successful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["username", "password"])
        for account in successful:
            writer.writerow(
                [
                    account.username,
                    account.password,
                ]
            )

    with open(f"output/{t}_reset_password_unsuccessful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["username", "error"])
        for account, error in unsuccessful:
            writer.writerow([account.username, error])
