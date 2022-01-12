import urllib.parse

import aiohttp


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

    def generate_password(self) -> str:
        return (
            self.username[0].upper()
            + self.username[1:-1]
            + self.username[-1].upper()
            + len(self.username)
            + "$$"
        )


class WHMAPI:
    server: str
    port: int
    username: str
    token: str
    version: int

    def __init__(
        self, server: str, port: int, username: str, token: str, version: int = 1
    ):
        self.server = server
        self.port = port
        self.username = username
        self.token = token
        self.version = version

    def api_url(self, endpoint: str) -> str:
        return f"https://{ self.server }:{ self.port }/json-api/{ endpoint }"

    def _call(self, session: aiohttp.ClientSession, endpoint: str, params: list[tuple]):
        url = self.api_url(endpoint)
        headers = {"Authorization": f"whm { self.username }:{ self.token }"}
        params.append(("api.version", self.version))
        return session.request("GET", url, headers=headers, params=params)

    def create_account(
        self, session: aiohttp.ClientSession, account: Account, plan: str
    ):
        account.domain = f"{ account.username }.{ self.server }"

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

    def remove_certificate(self, session: aiohttp.ClientSession, domain: str):
        params = [
            ("cpanel.function", "delete_ssl"),
            ("cpanel.module", "SSL"),
            ("cpanel.user", domain["username"]),
            ("domain", domain["domain"]),
        ]
        return self._call(session, "uapi_cpanel", params)

    def add_certificate(
        self,
        session: aiohttp.ClientSession,
        domain: str,
        crt: str,
        key: str,
        cabundle: str,
    ):
        params = [
            ("cpanel.function", "install_ssl"),
            ("cpanel.module", "SSL"),
            ("cpanel.user", domain["username"]),
            ("domain", domain["domain"]),
            ("cert", crt),
            ("key", key),
            ("cabundle", cabundle),
        ]
        return self._call(session, "uapi_cpanel", params)

    def redirect_https(self, session: aiohttp.ClientSession, domain: str):
        params = [
            ("cpanel.function", "toggle_ssl_redirect_for_domains"),
            ("cpanel.module", "SSL"),
            ("cpanel.user", domain["username"]),
            ("domains", domain["domain"]),
            ("state", 1),
        ]
        return self._call(session, "uapi_cpanel", params)
