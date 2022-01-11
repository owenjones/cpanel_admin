import os
import csv
import asyncio

from dotenv import load_dotenv
import aiohttp

load_dotenv()
server = os.getenv("WHMSERVER", "127.0.0.1")
port = os.getenv("WHMPORT", "2087")


class Account:
    rawusername: str
    username: str
    email: str
    password: str
    domain: str

    def __init__(self, username: str, email: str):
        self.rawusername = username
        self.username = username.replace("-", "")

        if len(self.username) > 16:
            raise Exception(f"Account username too long: { self.username }")

        self.email = email.lower()
        self.password = self.generate_password()
        self.domain = f"{ self.username }.{ server }"

    def generate_password(self) -> str:
        return self.username[0].upper() + self.username[1:] + "$$"


class WHMAPI:
    username: str
    token: str
    version: int

    def __init__(self, username: str, token: str, version: int = 1):
        self.username = username
        self.token = token
        self.version = version

    @staticmethod
    def api_url(endpoint: str) -> str:
        return f"https://{ server }:{ port }/json-api/{ endpoint }"

    def _call(self, session: aiohttp.ClientSession, endpoint: str, params: list[tuple]):
        url = WHMAPI.api_url(endpoint)
        headers = {"Authorization": f"whm { self.username }:{ self.token }"}
        params.append(("api.version", self.version))
        return session.get(url, headers=headers, params=params)

    def create_account(
        self, session: aiohttp.ClientSession, account: Account, plan: str
    ):
        return self._call(
            session,
            "createacct",
            [
                ("domain", account.domain),
                ("username", account.username),
                ("password", account.password),
                ("contactemail", account.email),
                ("plan", plan),
            ],
        )


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
            async with api.create_account(session, account, plan) as response:
                status = await response.json(content_type="text/plain")

                if status["metadata"]["result"] == 1:
                    successful.append(account)
                else:
                    unsuccessful.append((account, status["metadata"]["reason"]))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="bulk add accounts to cPanel")
    parser.add_argument(
        "input", type=str, help="csv file to load input usernames and emails from"
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store_true",
        help="save csv output for successful and unsuccessful account creations",
    )
    parser.add_argument(
        "-p",
        "--plan",
        type=str,
        default="default",
        help="the cPanel plan (package) to create the account with",
    )
    parser.add_argument("-v", "--debug", action="store_true")
    args = parser.parse_args()

    api = WHMAPI(os.getenv("WHMUSER"), os.getenv("WHMTOKEN"))
    accounts = load_accounts(args.input)
    successful = []
    unsuccessful = []
    asyncio.run(create_accounts(api, accounts, args.plan, successful, unsuccessful))

    print(
        f"Run finished: { len(successful) } accounts created successfully under plan { args.plan }."
    )

    if len(unsuccessful) > 0:
        print(f"There was a problem creating { len(unsuccessful) } account(s):\n")
        for account, error in unsuccessful:
            print(f"{ account.username } - { error }")

    if args.output:
        if not os.path.exists("output"):
            os.makedirs("output")

        with open("output/successful.csv", "w") as output:
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

        with open("output/unsuccessful.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["username", "email", "error"])
            for account, error in unsuccessful:
                writer.writerow([account.username, account.email, error])
