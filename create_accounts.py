import csv
import asyncio

import aiohttp

from whmapi import Account, WHMAPI


def load_accounts(file: str) -> list[Account]:
    accounts = []

    with open(file) as input:
        rows = csv.DictReader(input)
        for row in rows:
            accounts.append(Account(row["username"], row["email"]))

    return accounts


async def create_accounts(
    api: WHMAPI,
    accounts: list[Account],
    plan: str,
    successful: list,
    unsuccessful: list,
):
    async with aiohttp.ClientSession() as session:
        for account in accounts:
            try:
                async with api.create_account(session, account, plan) as response:
                    status = await response.json(content_type="application/json")

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

    parser = ArgumentParser(description="bulk add accounts to cPanel")
    parser.add_argument(
        "input", type=str, help="csv file to load input usernames and emails from"
    )
    parser.add_argument(
        "--plan",
        "-p",
        type=str,
        default="default",
        help="the cPanel plan (package) to create the account with",
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
    asyncio.run(create_accounts(api, accounts, args.plan, successful, unsuccessful))

    debug(
        f"Run finished: { len(successful) } accounts created successfully under plan { args.plan }."
    )

    if len(unsuccessful) > 0 and args.debug:
        debug(f"There was a problem creating { len(unsuccessful) } account(s):\n")
        for account, error in unsuccessful:
            debug(f"{ account.username } - { error }")

    t = int(time.time())
    with open(f"output/{t}_create_successful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["uwe_username", "username", "password", "domain", "email"])
        for account in successful:
            writer.writerow(
                [
                    account.rawusername,
                    account.username,
                    account.password,
                    account.domain,
                    account.email,
                ]
            )

    with open(f"output/{t}_create_unsuccessful.csv", "w") as output:
        writer = csv.writer(output)
        writer.writerow(["username", "email", "error"])
        for account, error in unsuccessful:
            writer.writerow([account.username, account.email, error])
