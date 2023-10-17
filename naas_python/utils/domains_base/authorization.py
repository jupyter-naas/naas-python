import asyncio
import json
import logging
import os
import socket
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import requests
import urllib3

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@dataclass
class TokenResponse:
    code: str = None
    client_id: str = ""
    request_signature: str = ""
    grant_type: str = "access_token"

    @property
    def raw(self):
        """Returns the dict representation of the object"""
        return self.__dict__


class CustomHandler(BaseHTTPRequestHandler):
    """
    Custom request handler for handling HTTP POST and OPTIONS requests.
    """

    def do_POST(self):
        """
        Handle HTTP POST request.
        """
        logging.debug("POST request received.")

        # Send a successful response header
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        # Inform the client that authentication is complete
        self.wfile.write(b"Authentication process has been successfully completed.")

        post_data = self._read_post_data()

        if post_data:
            data = json.loads(post_data.decode("utf-8"))
            self.server.set_data(data)
            logging.debug(f"Received POST data: {data}")
        else:
            logging.debug("No POST data received.")

    def _read_post_data(self):
        # Extract the content length from the request headers
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            return self.rfile.read(content_length)
        return None

    def do_OPTIONS(self):
        """
        Handle HTTP OPTIONS request.
        """
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        }

        # Send a successful response header and include CORS headers
        self.send_response(200)
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()

        # Log that an OPTIONS request was received
        logging.debug("OPTIONS request received.")


class AuthenticatorBaseServer(ThreadingHTTPServer):
    data = {}

    def __init__(self, hostname, port, timeout):
        super().__init__((hostname, port), CustomHandler)
        self.timeout = timeout

    def set_data(self, data: TokenResponse or dict):
        if isinstance(data, dict):
            # act as a validator
            self.data = TokenResponse(**data).raw
        else:
            self.data = data.raw

    def handle_timeout(self):
        self.server_close()

    def _gather_result(self):
        while not self.data:
            try:
                self.handle_request()
            except IOError:
                self._handle_exception(400, "invalid_request", "IOError")
                break
            except Exception as e:
                self._handle_exception(500, "server_error", "Internal Server Error")
                break

        if not self.data:
            self._handle_exception(408, "timeout", "Request timed out.")

        return self.data

    def _handle_exception(self, status, error, error_description):
        # I kept the status here for future API compatibility
        self.data.update(
            {
                "error": error,
                "error_description": error_description,
            }
        )


class IAuthenticatorAdapter:
    @classmethod
    def trade_for_long_lived_token(cls, access_token):
        raise NotImplementedError

    @classmethod
    def check_credentials(cls):
        raise NotImplementedError

    @property
    def access_token(self):
        raise NotImplementedError

    @property
    def jwt_token(self):
        raise NotImplementedError


class NaasSpaceAuthenticatorAdapter(IAuthenticatorAdapter):
    def __init__(
        self,
        port=8080,
        trade_url="https://auth.naas.ai/bearer/workspace/longlived",
        timeout=60,
        login_url="https://naas.ai?cli_token=generate_token",
    ):
        self._access_token = None
        self._jwt_token = None
        self.port = port
        self._server = None
        self._timeout = timeout
        self.trade_url = trade_url
        self._login_url = login_url
        self._redirect_uri = None

    def _start_http_server(self, start_port) -> AuthenticatorBaseServer:
        port = start_port

        for port in range(start_port, start_port + 1000):
            try:
                self._server = AuthenticatorBaseServer(
                    "localhost", self.port, timeout=self._timeout
                )
                logging.debug(f"HTTP server started on port {self.port}.")
                self._redirect_uri = f"http://localhost:{port}"
                break
            except socket.error:
                continue
            except Exception as e:
                print(e)
                break

        if self._redirect_uri is None:
            logging.debug("No available ports found.")
            return None

        if not self._server:
            logging.debug("Failed to start HTTP server.")
            return None
        else:
            return self._server

    # This method is intended for use in mock testing only, not for production.
    def _handle_mock_post(self, data: dict):
        """
        Replicates the behavior of an external agent by submitting a POST request to the server.

        :param data: A dictionary containing data to be sent in the request.
        :return: The response from the server.
        """
        try:
            # Define a function for sending the POST request asynchronously
            async def send_post_request():
                try:
                    # Create a connection pool using urllib3
                    with urllib3.PoolManager() as http:
                        response = http.request(
                            "POST", self._redirect_uri, body=json.dumps(data)
                        )
                        post_result = response.data
                    return post_result
                except Exception as e:
                    raise e

            # Create a ThreadPoolExecutor to run _gather_results in a separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                loop = asyncio.get_event_loop()

                # Use asyncio to run _gather_results in a separate thread
                _gather_results_future = loop.run_in_executor(
                    executor, self._server._gather_result
                )

                # Asynchronously send the POST request
                post_result = loop.run_until_complete(send_post_request())

                assert (
                    post_result
                    == b"Authentication process has been successfully completed."
                )

                # Wait for _gather_results to complete
                _gather_result = loop.run_until_complete(_gather_results_future)

                return _gather_result
        except Exception as e:
            # Handle exceptions or log errors as needed
            return f"Error: {str(e)}"

    def _parse_login_response(self, response):
        if response.get("error"):
            raise Exception(
                f"Error {response.get('status')}: {response.get('error_description')}"
            )

        if not response.get("code"):
            raise Exception("No code received.")

        return response.get("code")

    def _request_token(self):
        # Get the access token from the NaaS authentication service
        with self._start_http_server(self.port) as server:
            # response = server._gather_result()

            _environment_mode = os.getenv("NAAS_ENVIRONMENT_MODE", "production")
            if _environment_mode == "production":
                if not webbrowser.open(self._login_url):
                    logging.debug("Failed to open the browser.")
                    return None
                response = server._gather_result()

            else:
                # In a non-production environment (test), send a mock POST request
                logging.debug(
                    "Running in a non-production environment. Sending a mock POST request."
                )
                try:
                    response = self._handle_mock_post(
                        TokenResponse(code="1f3aa7383589491b9ed2f14cb4e2ab50").raw
                    )
                    logging.info(f"Mock response: {response}")
                except Exception as e:
                    raise e

            if not response:
                logging.debug("No response received.")
                return None

        access_token = self._parse_login_response(response)
        # Proceed with registering the token into the credentials file (following the model described above)
        return access_token

    @property
    def access_token(self):
        if self._access_token is None:
            self._access_token = self._request_token()
        return self._access_token

    def _gather_env_credentials(self):
        _SCHEMA_VARS = {
            "NAAS_CREDENTIALS_JWT_TOKEN": "jwt_token",
        }

        credentials = {}

        for key, value in _SCHEMA_VARS.items():
            if os.getenv(key):
                credentials[value] = os.getenv(key)

        # Run contents validation...
        return credentials

    def _gather_file_credentials(self, credentials_file_path: Path):
        with open(credentials_file_path, "r") as file:
            self._file_contents = file.read()
            # If file is "encoded/encrypted" run decoding/decryption process
            # ...
        # Run contents validation...
        return self._file_contents

    def _generate_credential_file(self, credentials_file_path: Path):
        # Trade access token (and authenticate) and store the long-lived token in the credentials file

        self._jwt_token = self.trade_for_long_lived_token(self.access_token)

        with open(credentials_file_path, "w") as file:
            file.write(json.dumps({"jwt_token": self._jwt_token}))

        return self._jwt_token

    def check_credentials(self):
        # This method is responsible for inspecting the naas credentials files
        # locally and retrieving the jwt token if it exists and is valid.
        # The order of priority is as follows:
        # 1. Check if file exists, if not call appropriate method to start authentication process
        # 2.a Check if file is empty, if so call appropriate method to start authentication process
        # 2.b If file is not empty, check if token is valid, if not call appropriate method to start authentication process
        # 3. If file exists and is not empty and token is valid, set the jwt token to the class property and return

        credentials_path = Path(os.path.expanduser("~/.naas/credentials"))

        if credentials_path.exists() and credentials_path.is_file():
            # First order option for credential gathering is to check the file contents and grab the token
            credentials = self._gather_file_credentials(credentials_path)
            logging.debug(
                f"Credentials file found and not empty. Contents are  {credentials}"
            )
            credentials.update(self._gather_env_credentials())

            # If environment variable is present, override file contents
            if "jwt_token" in credentials:
                # Validate stored token is valid... then assign value and return
                self._jwt_token = credentials["jwt_token"]
                return self._jwt_token

        else:
            # As a second order option, look for the existence of overriding environment variable to create the new file
            _var_credentials = self._gather_env_credentials()

            if "jwt_token" in _var_credentials:
                # Validate stored token is valid... then assign value and return
                self._jwt_token = _var_credentials["jwt_token"]
                return self._jwt_token

            # We could not find any credentials, so we need to start the authentication process
            self._generate_credential_file(credentials_file_path=credentials_path)

        if not self._jwt_token:
            raise Exception("Could not find any credentials to authenticate with.")

    def trade_for_long_lived_token(self, access_token, token_type: str = "jupyterhub"):
        # headers = {"Authorization": f"Bearer {access_token}"}
        if token_type == "jupyterhub":
            self.trade_url = (
                f"https://auth.naas.ai/bearer/jupyterhubtoken/?token={access_token}"
            )

        response = requests.get(self.trade_url)

        if response.status_code == 200:
            result = response.text
            logging.debug("Token successfully traded for long-lived token.")
            return json.loads(result).get("access_token")
        else:
            print(response)
            raise Exception("Token trade failed.")

    @property
    def jwt_token(self):
        if self._jwt_token:
            return self._jwt_token
        else:
            # Check credentials which is responsible for gathering token
            # (from credentials file or authentication process)
            self.check_credentials()
            return self._jwt_token

    # def main(self):
    #     token = self.access_token
    #     # Continue with other CLI operations
    #     print("My token is: ", token)

    #     # Check jwt_token
    #     jwt = self.jwt_token
    #     print("My jwt_token is: ", jwt)

    #     # Remove credentials file
    #     credentials_path = Path(os.path.expanduser("~/.naas/credentials"))
    #     if credentials_path.exists() and credentials_path.is_file():
    #         credentials_path.unlink()
    #         print("Credentials file removed.")
    #     else:
    #         print("Credentials file not found.")
