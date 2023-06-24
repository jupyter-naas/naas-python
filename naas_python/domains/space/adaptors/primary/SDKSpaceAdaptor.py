from ...SpaceSchema import ISpaceInvoker, ISpaceDomain, NAASCredentials
from naas_python.domains.authorization import write_token_to_file, load_token_from_file

from pathlib import Path


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def add(self):
        print("SDKSpaceAdaptor add called")
        self.domain.add()

    def list(self):
        print("SDKSpaceAdaptor list called")

    def credentials(token: str = None):
        if (
            not token
            and (credentials_file := Path.home() / ".naas" / "credentials").exists()
        ):
            token = load_token_from_file(credentials_file)

        elif token:
            write_token_to_file(token)

        # Use the token value as required
        if not token:
            raise Exception(
                "Missing NAAS token; pass 'token' or set NAAS_TOKEN as an environment variable"
            )

        return NAASCredentials(token=token)
