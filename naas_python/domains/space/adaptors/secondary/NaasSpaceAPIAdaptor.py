from ...SpaceSchema import ISpaceAdaptor

import requests
import uuid


class NaasSpaceAPIAdaptorException(BaseException):
    pass


class NaasSpaceAPIAdaptor(ISpaceAdaptor):
    def __init__(self) -> None:
        super().__init__()
        self.host = "http://localhost:8000"

    def add(self):
        print("NaasSpaceAPIAdaptor add called")

    def create(self, name: str, namespace: str, image: str):
        print("NaasSpaceAPIAdaptor create called")

        try:
            print(
                f"Creating space with the following details: {name}, {namespace}, {image}"
            )
            api_response = requests.post(
                f"{self.host}/space/",
                json={
                    "name": name,
                    "namespace": namespace,
                    "image": image,
                    "user_id": str(uuid.uuid4()),
                },
            )
            # print response contents and header
            print(f"Headers: {api_response.headers} \n Content: {api_response.content}")
            print(api_response.status_code)
            json_body = api_response.json()
            if api_response.status_code == 201 and json_body.get("status") == "Success":
                return json_body.get("space")

            elif (
                api_response.status_code == 409 and json_body.get("status") == "Failure"
            ):
                return json_body.get("message")

            else:
                print("Space creation failed")
                raise NaasSpaceAPIAdaptorException("An untracked error occurred")

        except NaasSpaceAPIAdaptorException as e:
            print(e)
            raise e
