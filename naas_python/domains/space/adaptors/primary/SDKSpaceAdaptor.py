import os

from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    NaasSpaceError,
    Space,
)
from naas_python.utils.domains_base.authorization import (
    NAASCredentials,
    load_token_from_file,
)


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def add(self):
        print("SDKSpaceAdaptor add called")
        self.domain.add()

    def create(
        self,
        name: str,
        namespace: str,
        image: str,
        user_id: str,
        env: dict,
        resources: dict,
    ):
        try:
            space = self.domain.create(
                name=name,
                namespace=namespace,
                image=image,
                user_id=user_id,
                env=env,
                resources=resources,
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def get(self, name: str, namespace: str):
        try:
            space = self.domain.get(name=name, namespace=namespace)
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def list(self, user_id: str, namespace: str):
        try:
            space = self.domain.list(user_id=user_id, namespace=namespace)
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def delete(self, name: str, namespace: str):
        try:
            self.domain.delete(name=name, namespace=namespace)
        except Exception as e:
            print(e)
            raise e

    def update(
        self,
        name: str,
        namespace: str,
        image: str,
        env: dict,
        resources: dict,
        cpu: str,
        memory: str,
    ):
        try:
            space = self.domain.update(
                name=name,
                namespace=namespace,
                update_patch={
                    "image": image,
                    "cpu": cpu,
                    "memory": memory,
                    "env": env,
                    "resources": resources,
                },
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()
