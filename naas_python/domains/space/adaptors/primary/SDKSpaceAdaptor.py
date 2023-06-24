from ...SpaceSchema import ISpaceInvoker, ISpaceDomain, NAASCredentials
from naas_python.domains.authorization import write_token_to_file, load_token_from_file

from pathlib import Path
import os


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def add(self):
        print("SDKSpaceAdaptor add called")
        self.domain.add()

    def list(self):
        print("SDKSpaceAdaptor list called")

    def credentials(self, token: str = None) -> NAASCredentials:
        """
        Retrieves the NAAS credentials.

        If the `token` parameter is not provided, it attempts to load the token
        from the credentials file. If the file is not found or does not contain
        a valid token, an exception is raised.

        Args:
            token (str, optional): Authorization token for NAAS. Defaults to the value of
                the 'NAAS_TOKEN' environment variable.

        Returns:
            NAASCredentials: NAAS credentials.

        Raises:
            Exception: If the token is missing and cannot be loaded from the credentials file.
        """
        if not token:
            if os.environ.get("NAAS_TOKEN"):
                token = os.environ.get("NAAS_TOKEN")
            else:
                token = load_token_from_file()
        return NAASCredentials(token=token)
