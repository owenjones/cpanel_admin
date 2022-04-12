import os
import csv
import asyncio

from dotenv import load_dotenv
import aiohttp

from whmapi import WHMAPI


def load_domains(file: str) -> list[dict]:
    domains = []

    with open(file) as input:
        rows = csv.DictReader(input)
        for row in rows:
            domains.append({"username": row["username"], "domain": row["domain"]})

    return domains


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

                    if status["metadata"]["result"] == 1:
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
                        unsuccessful.append(
                            (domain["domain"], status["metadata"]["reason"])
                        )

            except Exception as e:
                unsuccessful.append((domain, e))


if __name__ == "__main__":
    load_dotenv()
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="bulk update SSL certificates on cPanel accounts"
    )
    parser.add_argument(
        "input", type=str, help="csv file to load usernames and domains from"
    )
    parser.add_argument(
        "--output",
        "-o",
        action="store_true",
        help="save csv output for successful and unsuccessful SSL certificate fixes",
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
    domains = load_domains(args.input)
    successful = []
    unsuccessful = []
    asyncio.run(
        fix_ssl(
            api,
            domains,
            os.getenv("SSLCRT"),
            os.getenv("SSLKEY"),
            os.getenv("SSLCAB"),
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

    if args.output:
        if not os.path.exists("output"):
            os.makedirs("output")

        with open("output/successful_ssl.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["domain"])
            for domain in successful:
                writer.writerow([domain["domain"]])

        with open("output/unsuccessful_ssl.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["domain", "error"])
            for domain, error in unsuccessful:
                writer.writerow([domain, error])
